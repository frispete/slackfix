#
# spec file for package slackfix
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           slackfix
Version:        0.1
Release:        0
Summary:        Slackfix Wrapper Script
License:        GPL-2.0-only
Group:          Productivity/Networking/Other
URL:            https://github.com/frispete/%{name}
Source:         %{name}-%{version}.tar.gz
BuildRequires:  python3-setuptools
BuildRequires:  systemd-rpm-macros
BuildArch:      noarch

%description
Wrapper script, attempts to execute Slack with the correct URI argument.

%prep
%setup -q
# shebang not needed at this point
sed -i '1!b;/^#!\/usr\/bin\/python/d' %{name}.py

%build
python3 setup.py build

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{python3_sitelib}/{,__pycache__/}%{name}*

%changelog
