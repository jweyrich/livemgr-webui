%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:           livemgr-webui
Version:        1.0
Release:        1%{?dist}
Summary:        Web interface for Live Manager

Group:          Development/Languages
License:        Live Manager Ltda.
URL:            https://github.com/jweyrich/livemgr-webui
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-setuptools
BuildRequires:  python-devel
Requires:       Django = 1.2.3
Requires:       django-tables >= 0.3
Requires:       python-reportlab
Requires:       m2crypto
Requires:       MySQL-python
Requires:       httpd
Requires:       mod_wsgi

%description
Web interface for Live Manager.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}

for d in templates media; do
    cp -r ${d} ${RPM_BUILD_ROOT}%{_datadir}/%{name};
done

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d
install -p -m 644 conf/webui-httpd.conf ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
#%doc
%{python_sitelib}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf

%changelog
* Wed Dec 01 2010 Jardel Weyrich <jweyrich@gmail.com> - 1.0-1
- initial packaging
