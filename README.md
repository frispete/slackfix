Slackfix
========

Wrapper script, attempts to execute Slack with the correct URI argument.

The electron environment in Tumbleweed seems to suffer from a flaw similar to
kde-open5 [1], that results in Slack failing to open the workspace correctly.
It mangles the host part of the URI into lowerspace, which is Slack's undoing.

Background
----------
Generic URL handling is defined in RFC 3986: URI Generic Syntax, where
section 3.2.2 says: "The host subcomponent is case-insensitive"). The electron
environment appears to conform with that in newer releases.

The simplest place to solve this would be also on the Slack side by accepting a
lower case host part of the internal slack:// URI, or it shouldn't use any host
part at all (slack:///...).

Since they are aware of this issue since several month, we cannot rely on a
fix provided anytime soon [3], so here's a (hopefully) suitable antidote.

External resources
------------------
[1] KDE issue: https://bugs.kde.org/show_bug.cgi?id=429408
[2] https://www.rfc-editor.org/rfc/rfc3986
[3] With the usual outcome: we do not support openSUSE Tumbleweed, use the
    snap packages! Needless to say, they suffer from the same issue.
    
