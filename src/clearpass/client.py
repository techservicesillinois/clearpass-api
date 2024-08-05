import logging
import re
import requests
import json
import urllib.parse

from clearpass.exceptions import TokenError

# ** Documentation **
# https://cplab.techservices.illinois.edu/api-docs

logger = logging.getLogger(__name__)

macaddress1 = re.compile(
    r'''^[0-9a-f]{12}$''')                     # e.g., A1B2C3D4E5F6
macaddress2 = re.compile(
    r'''^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$''')   # e.g., A1:B2:C3:D4:E5:F6
macaddress3 = re.compile(
    r'''^(?:[0-9a-f]{4}\.){2}[0-9a-f]{4}$''')  # e.g., A1B2.C3D4.E5F6
macaddress4 = re.compile(
    r'''^(?:[0-9a-f]{2}\-){5}[0-9a-f]{2}$''')  # e.g., A1-B2-C3-D4-E5-F6


# Make sure that any mac address is properly formatted
def normalize_mac_address(macstring):
    m = macstring.lower()
    if macaddress1.match(m):
        return m
    if macaddress2.match(m):
        return re.sub(r''':''', '', m)
    if macaddress3.match(m):
        return re.sub(r'''\.''', '', m)
    if macaddress4.match(m):
        return re.sub(r'''\-''', '', m)
    return None


# Convert an all lowercase mac to a hyphenated string of macs
def hyphenate_mac(macstring):
    m = normalize_mac_address(macstring)
    if not m:
        logger.warning(f"Hyphenating {macstring} failed")
        return macstring
    evenchar = True
    retmac = ""
    for char in m:
        evenchar = not evenchar
        retmac += char
        if evenchar:
            retmac += "-"
    return retmac.upper()[:-1]


class APIConnection():
    def __init__(self, username, password, endpoint, client_id, client_secret):
        self._baseurl = f"https://{endpoint}/"

        self._authurl = f"{self._baseurl}api/oauth"
        self._authpayload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        self._getheaders = None
        self._postheaders = None

        self._macinfo = {}

    def _get_access_token(self):
        res = requests.post(
            url=self._authurl,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(self._authpayload),
            verify=False,
        )
        if res.status_code != 200:
            logger.warning("Request for authentication returned HTTP "
                           f"{res.status_code}: {res.reason}")
            if res.status_code < 200 or res.status_code > 299:
                raise TokenError()
        retjson = res.json()
        return retjson["access_token"]

    def test_connectivity(self):
        try:
            self._get_access_token()
            return True
        except Exception:
            return False

    @property
    def getheaders(self):
        if self._getheaders:
            return self._getheaders

        token = self._get_access_token()
        self._getheaders = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        return self._getheaders

    @property
    def postheaders(self):
        if self._postheaders:
            return self._postheaders

        self._postheaders = {'Content-Type': 'application/json'}
        self._postheaders.update(self.getheaders)
        return self._postheaders

    def _put_api(self, resource, payload):
        return requests.put(
            url=f"{self._baseurl}api/{resource}",
            headers=self.postheaders,
            data=json.dumps(payload),
            verify=False,
        )

    def _get_api(self, resource, filter=None):
        url = f"{self._baseurl}api/{resource}"
        if filter:
            url += f"?filter={urllib.parse.quote(json.dumps(filter))}"

        return requests.get(
            url=url,
            headers=self.getheaders,
            verify=False,
        )

    def get_info_for_mac_address(self, mac, filter={}):
        if mac not in self._macinfo:
            ret = {}
            rmacfilter = {"mac_address": mac}
            hmacfilter = {"mac": hyphenate_mac(mac)}
            data = {}

            data["endpointinfo"] = ("endpoint", rmacfilter)
            data["deviceinfo"] = ("device", hmacfilter)
            data["guestinfo"] = ("guest", hmacfilter)
            data["sessioninfo"] = ("session", rmacfilter)
            data["insightinfo"] = (f"insight/endpoint/mac/{mac}", None)

            for name, (resource, filter) in data.items():
                info = self._get_api(resource, filter=filter)
                if info.status_code == 200:
                    if name == "insightinfo":
                        ret[name] = [info.json()]
                    else:
                        ret[name] = info.json()["_embedded"]["items"]
                else:
                    logger.warning(
                        f"{name}: HTTP {info.status_code} - {info.reason}")

            self._macinfo[mac] = ret
        return self._macinfo[mac]

    def get_mac_id(self, mac):
        mac_info = self._get_api(f"endpoint/mac-address/{mac}").json()
        try:
            return mac_info["id"]
        except KeyError:
            raise ValueError(f"MAC address {mac} not found on server")

    def set_mac_address(
            self, mac_id, mac, status, description=None, attributes=None):
        data = {
            "id": mac_id,
            "mac_address": mac,
            "status": status
        }
        if description is not None:
            data["description"] = description

        if attributes is not None:
            data["attributes"] = attributes
        return self._put_api(f"endpoint/{mac_id}", data)

    def enable_mac_address(self, mac):
        mac_id = self.get_mac_id(mac)
        res = self.set_mac_address(mac_id, mac, status="Known")
        if res.status_code == 404:
            raise ValueError(f"{mac} not found.")
        return res

    def disable_mac_address(self, mac, disabled_by, reason):
        mac_id = self.get_mac_id(mac)
        res = self.set_mac_address(
            mac_id, mac, status="Disabled",
            attributes={
                "Disabled By": disabled_by,
                "Disabled Reason": reason
            })
        if res.status_code == 404:
            raise ValueError(f"{mac} not found.")
        return res
