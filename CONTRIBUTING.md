## Translation Table for Disconnect JSON Response

When calling `disconnect_mac_address`, `count`, `count_success` and `count_failed` may be returned.

When `count` is `0`, no active session was found. This is a success,
since the `mac` is not connected.

Otherwise, look for `count_success` or `count_failed`.

    count - 0 - no active session found (success)
    count - 1 - count_success 1 = found and disconnected active session
    count - 1 - count_failed 1 = found active session, but could not disconnect

The test device disconnects and reconnects every 30 seconds or so. There may not always be an active session to disconnect.

Sometimes the attempt to pro-actively disconnect comes too late, as the device was already logging out on it's own, or because the previous ban happened to catch it earlier, and before our second call to disconnect the session can reach the API.

These are still success cases, as the device is successfully disconnected, preventing any further malicious traffic from it.
