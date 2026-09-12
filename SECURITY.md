# Security

This firmware has no network stack. The ESP32 on this board has Wi-Fi and this
firmware never switches the radio on, never opens a socket, and never stores a
credential. Nothing leaves the device except what is printed to a USB serial
console. There is no remote attack surface to report against.

## What is worth reporting

**A measurement bug.** The way this project can do harm is by telling somebody
the air is fine when it is not. A misparsed frame that silently reports stale
particulate figures, a CO2 calibration that pins the baseline at the wrong
value, an averaging fault that hides a spike — any of those could leave a person
sitting in a room they would otherwise have ventilated. Treat that class of bug
as a safety issue and report it, even though none of it is a security
vulnerability in the ordinary sense.

This is a hobby instrument. It is not a workplace exposure monitor, not a fire or
gas alarm, and not a medical device, and it must not be relied on as one. It
cannot detect carbon **monoxide**, which is the gas that kills people in homes —
buy a certified CO alarm for that, and do not let a box full of sensors give you
the impression you already have one.

## Lithium cells

The cell is charged by the board's own circuitry, not by anything in this
repository. If you find an instruction in these documents that would lead
somebody to wire or charge a cell dangerously — reversed polarity into the JST
connector being the obvious one — that is worth reporting too.

## How to report

Use [GitHub's private vulnerability
reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository. For an ordinary measurement bug a normal issue is fine and
easier to discuss in the open.

## What to expect

There is no support commitment and no CVE process. Reports are read in good
faith; fixes depend on maintainer time and on how badly the bug misleads.
