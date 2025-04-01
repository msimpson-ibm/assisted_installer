# -*- coding: utf-8 -*-
# Copyright (c) 2023, Alberto Gonzalez <alberto.gonzalez@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
import requests


def _get_access_token(*args, client_id=None, client_secret=None):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    if len(args) == 1 and not (client_id or client_secret):
        # Single argument, treat as offline token
        offline_token = args[0]
        data = {
            "grant_type": "refresh_token",
            "client_id": "cloud-services",
            "refresh_token": offline_token
        }
    elif client_id and client_secret:
        # Client credentials flow
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    else:
        raise ValueError("Provide either just offline_token or both client_id and client_secret")

    response = requests.post(
        "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token",
        headers=headers,
        data=data
    )
    return response


def main():
    # Using offline token (just one argument)
    print(_get_access_token("REPLACEME_OFFLINE_TOKEN").json())

    # Using client credentials
    # print(_get_access_token(client_id="myclient", client_secret="mysecret").json())


if __name__ == "__main__":
    main()
