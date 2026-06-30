# Local control — can the hood run without the cloud? (No)

A natural question for a cloud-dependent integration: can the hood be pointed at a
**local MQTT broker** so it works without AWS? This was investigated on a live
network on **2026-06-30**. The answer is **no — not in software.**

## What was tested

The hood (a **Gemtek** Wi-Fi module, model **ZVE-E36DS**) talks only to **AWS IoT
Core** — `a1nqxu0hki9zw3-ats.iot.us-west-2.amazonaws.com:8883`, MQTT **Device
Shadow** — and it was probed end-to-end:

1. **It pins/validates the AWS server certificate.** Its `:8883` traffic was
   transparently redirected to a local TLS listener presenting a self-signed cert.
   Reproducibly, the hood:
   - sent its `ClientHello`,
   - received our `ServerHello` + `Certificate` (self-signed) + `ServerHelloDone`,
   - then **immediately closed the connection (FIN) — before sending its
     `ClientKeyExchange`/client certificate**, i.e. it aborts at exactly the point
     where a TLS client validates the *server* certificate.

   So it refuses any server whose cert does not chain to the CA it trusts (Amazon
   Root CA). A DNS/redirect to a local broker (Mosquitto / Zigbee2MQTT's broker)
   **cannot work** — there is no cert we can present that it will accept.

2. **It exposes no local network services.** A full **TCP 1–65535** connect scan
   found nothing open; no **mDNS (5353)** or **SSDP/UPnP (1900)** response. It is a
   pure outbound-only client — there is no local API or web UI.

3. **Bluetooth** was not enumerated (needs a BT host next to the unit), but on these
   appliances BLE is typically **Wi-Fi onboarding only**, not an ongoing control
   channel.

## Conclusion

This integration is **cloud-dependent by necessity** — there is no local-only mode
for this hardware, and no way to intercept or relocate its MQTT. The only paths to
genuinely local control are **hardware** (replace the hood's Wi-Fi control board
with an ESP32 running ESPHome/Tasmota, wired into its control lines) or a firmware
modification of the Gemtek module (no flashing path; effectively infeasible) — both
outside the scope of this integration.

If local-first operation matters, prefer devices speaking Zigbee / Z-Wave / Matter
or ESPHome-friendly Wi-Fi over AWS-IoT-pinned cloud devices like this one.
