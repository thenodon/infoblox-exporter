# -*- coding: utf-8 -*-
"""
    Copyright (C) 2023 Anders Håål

    This file is part of infoblox_exporter.

    infoblox_exporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    infoblox_exporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with infoblox_exporter.  If not, see <http://www.gnu.org/licenses/>.

    The following functions are from the project https://github.com/prometheus/client_python and under license
    https://github.com/prometheus/client_python/blob/master/LICENSE. The reason they are copied is due to the async
    implementation in the infoblox_exporter
    - floatToGoString
    - generate_latest

"""

import os
import math
import secrets
import time
import uvicorn
import logging.config as lc
import logging

from fastapi import FastAPI, Response, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

from prometheus_client.exposition import CONTENT_TYPE_LATEST
from prometheus_client.registry import CollectorRegistry
from prometheus_client import Gauge

from infoblox_exporter.exceptions import InfobloxException
from infoblox_exporter.infoblox import InfobloxCollector
from infoblox_exporter.server_config import Settings

FORMAT = 'timestamp=%(asctime)s level=%(levelname)s module="%(module)s" msg="%(message)s"'
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

lc.dictConfig(
    {
        "version": 1,
        "formatters": {

            "logfmt": {
                "()": "logfmter.Logfmter",
                "keys": ['timestamp', 'level'],
                "mapping": {"level": "levelname", "timestamp": "asctime"},
                "datefmt": TIME_FORMAT
            }
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "logfmt"}
        },
        "loggers": {"": {"handlers": ["console"], "level": os.getenv('EXPORTER_LOG_LEVEL', 'INFO')}},
    }
)

app = FastAPI()
security = HTTPBasic()
global_settings = Settings()


def authorize(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(global_settings.basic_auth_username, 'utf-8')
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(global_settings.basic_auth_password, 'utf-8')
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


MIME_TYPE = 'text/html'
INF = float("inf")
MINUS_INF = float("-inf")
NaN = float("NaN")


def floatToGoString(d):
    d = float(d)
    if d == INF:
        return '+Inf'
    elif d == MINUS_INF:
        return '-Inf'
    elif math.isnan(d):
        return 'NaN'
    else:
        s = repr(d)
        dot = s.find('.')
        # Go switches to exponents sooner than Python.
        # We only need to care about positive values for le/quantile.
        if d > 0 and dot > 6:
            mantissa = '{0}.{1}{2}'.format(s[0], s[1:dot], s[dot + 1:]).rstrip('0.')
            return '{0}e+0{1}'.format(mantissa, dot - 1)
        return s


def generate_latest(metrics_list: list):
    """
    Returns the metrics from the registry in text format as a string
    :param metrics_list:
    :return:
    """
    """"""

    def sample_line(line):
        if line.labels:
            labelstr = '{{{0}}}'.format(','.join(
                ['{0}="{1}"'.format(
                    k, v.replace('\\', r'\\').replace('\n', r'\n').replace('"', r'\"'))
                    for k, v in sorted(line.labels.items())]))
        else:
            labelstr = ''
        timestamp = ''
        if line.timestamp is not None:
            # Convert to milliseconds.
            timestamp = ' {0:d}'.format(int(float(line.timestamp) * 1000))
        return '{0}{1} {2}{3}\n'.format(
            line.name, labelstr, floatToGoString(line.value), timestamp)

    output = []
    for metric in metrics_list:
        try:
            mname = metric.name
            mtype = metric.type
            # Munging from OpenMetrics into Prometheus format.
            if mtype == 'counter':
                mname = mname + '_total'
            elif mtype == 'info':
                mname = mname + '_info'
                mtype = 'gauge'
            elif mtype == 'stateset':
                mtype = 'gauge'
            elif mtype == 'gaugehistogram':
                # A gauge histogram is really a gauge,
                # but this captures the structure better.
                mtype = 'histogram'
            elif mtype == 'unknown':
                mtype = 'untyped'

            output.append('# HELP {0} {1}\n'.format(
                mname, metric.documentation.replace('\\', r'\\').replace('\n', r'\n')))
            output.append('# TYPE {0} {1}\n'.format(mname, mtype))

            om_samples = {}
            for s in metric.samples:
                for suffix in ['_created', '_gsum', '_gcount']:
                    if s.name == metric.name + suffix:
                        # OpenMetrics specific sample, put in a gauge at the end.
                        om_samples.setdefault(suffix, []).append(sample_line(s))
                        break
                else:
                    output.append(sample_line(s))
        except Exception as exception:
            exception.args = (exception.args or ('',)) + (metric,)
            raise

        for suffix, lines in sorted(om_samples.items()):
            output.append('# HELP {0}{1} {2}\n'.format(metric.name, suffix,
                                                       metric.documentation.replace('\\', r'\\').replace('\n', r'\n')))
            output.append('# TYPE {0}{1} gauge\n'.format(metric.name, suffix))
            output.extend(lines)
    return ''.join(output).encode('utf-8')


@app.get('/')
def alive():
    return Response("infoblox_exporter alive!", status_code=200, media_type=MIME_TYPE)


@app.get("/probe")
async def probe(target: str, module: str, auth: str = Depends(authorize)):
    start_time = time.time()

    if not target or target == "":
        return Response("Target must be specified", status_code=400, media_type=MIME_TYPE)

    # If target do not include a port number

    registry = CollectorRegistry()
    try:

        collector = InfobloxCollector(connection=global_settings.infoblox, target=target, module=module)
        registry.register(collector)

        duration = Gauge('infoblox_scrape_duration_seconds', 'Time spent processing request', registry=registry)

        duration.set(time.time() - start_time)

        infoblox_response = generate_latest(await collector.collect())

        duration.set(time.time() - start_time)
        return Response(infoblox_response, status_code=200, media_type=CONTENT_TYPE_LATEST)
    except InfobloxException as err:
        logging.error("Exporter failed", extra={'target': target, 'error': err})
        return Response(err.message, status_code=err.status, media_type=MIME_TYPE)
    except Exception as err:
        logging.error(f"Failed to create metrics", extra={'target': target, 'error': err})
        return Response(f"Internal server error for {target}- please check logs", status_code=500, media_type=MIME_TYPE)


def start():
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = FORMAT
    log_config["formatters"]["access"]['datefmt'] = TIME_FORMAT
    log_config["formatters"]["default"]["fmt"] = FORMAT
    log_config["formatters"]["default"]['datefmt'] = TIME_FORMAT
    log_config["loggers"]["uvicorn.access"]["level"] = os.getenv('EXPORTER_LOG_LEVEL', 'INFO')

    uvicorn.run(app, host=os.getenv('EXPORTER_HOST', "0.0.0.0"), port=os.getenv('EXPORTER_PORT', 9597),
                log_config=log_config)
