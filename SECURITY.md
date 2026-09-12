# Security

Out of the box this firmware opens no sockets and never switches the radio on.
Nothing leaves the device except what is printed to a USB serial console.

## Credentials

The monitor can optionally publish readings to ThingSpeak, and doing so means
putting a Wi-Fi password and a channel write key on the board in a `config.py`.
That file is in `.gitignore` and there are no credentials anywhere in this
repository. If you ever find one that has crept in — in a commit, in an issue,
in a screenshot in the documentation — please report it rather than opening a
pull request, so that it can be revoked before it is pointed at.

Two properties of the upload are worth knowing rather than reporting, because
they are how the service works rather than defects here: the request is plain
HTTP with the key in the URL, so anyone on the same network can read it; and
channel data is as public or private as you configure the channel to be.

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
