# Third-party code and license notices

## BreezySLAM RPLidar example

`src/controllers/mapping_test.py` is adapted from Simon D. Levy's BreezySLAM
[`examples/rpslam.py`](https://github.com/simondlevy/BreezySLAM/blob/0aadd46aaf9708bf7d708e1b67d75ff99b9ea8a0/examples/rpslam.py),
at revision `0aadd46aaf9708bf7d708e1b67d75ff99b9ea8a0` (13 January 2019).

Copyright (C) 2018 Simon D. Levy. The source specifies the GNU Lesser General
Public License, version 3 or any later version (`LGPL-3.0-or-later`). Its notice
is restored in the mapping source. Copies of [LGPL version 3](LICENSES/LGPL-3.0.txt)
and the [GPL version 3](LICENSES/GPL-3.0.txt) that it incorporates accompany this
repository.

Relative to that historical example, this project's original import increased
the map resolution from 500 to 1,000 pixels and changed the viewer-close path to
leave the loop and stop/disconnect the LiDAR before exiting. The cleanup on
22 October 2026 adds explicit configuration, deferred dependency loading and
device cleanup on failure/interruption, with tests using simulated dependencies.
The SLAM algorithm and original example remain upstream work.

The LGPL copy is from the same upstream revision's
[LICENSE.md](https://github.com/simondlevy/BreezySLAM/blob/0aadd46aaf9708bf7d708e1b67d75ff99b9ea8a0/LICENSE.md).
The accompanying GPL text is from the
[SPDX license list](https://github.com/spdx/license-list-data/blob/main/text/GPL-3.0-or-later.txt).

These notices cover the identified third-party example. They do not establish
a new repository-wide license for separately authored project code or audio.
External dependencies retain their own licenses. This repository previously had
no blanket project license, and this cleanup does not add one.
