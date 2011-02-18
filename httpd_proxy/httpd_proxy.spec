%define version 2.2.17
%define relver 9
%define dist my
%define prefix /usr/local/httpd_proxy

Summary: Apache HTTP Server
Name: httpd_proxy
Version: %{version}
Release: %{relver}.%{dist}
URL: http://httpd.apache.org/
Source0: http://www.apache.org/dist/httpd/httpd-%{version}.tar.bz2
Source1: mod_cidr_lookup-1.2.tar.gz
Source2: extract_forwarded-2.0.2.tar.gz
Source3: mod_bumpy_life.c
Source4: httpd_proxy.conf
Source5: httpd_proxy.init
Source6: httpd_proxy.sysconf
Source7: httpd_proxy_index.html
Source8: httpd_proxy_live.html
Source9: httpd_proxy.logrotate
Patch0: httpd_proxy_override_expires.patch
Patch1: httpd_proxy_mod_proxy_qretry.patch
License: Apache Software License
Group: System Environment/Daemons
Packager: nsg <nsg@livedoor.jp>

BuildRoot: %{_tmppath}/%{name}-root
BuildRequires: autoconf, perl, pkgconfig, xmlto >= 0.0.11, findutils
BuildRequires: db4-devel, expat-devel, zlib-devel, libselinux-devel openssl

Requires: /etc/mime.types, gawk, /usr/share/magic.mime, /usr/bin/find
Requires: initscripts >= 8.36
Prereq: /sbin/chkconfig, /bin/mktemp, /bin/rm, /bin/mv
Prereq: sh-utils, textutils, /usr/sbin/useradd

%description
http proxy

%prep
%setup -q -n httpd-%{version}
%patch0 -p1
%patch1 -p1

%build
cp %{SOURCE1} ./
tar zxf mod_cidr_lookup-1.2.tar.gz
cp %{SOURCE2} ./
tar zxf extract_forwarded-2.0.2.tar.gz
cp %{SOURCE3} ./
./configure \
    --prefix=%{prefix} \
    --with-mpm=worker \
    --with-program-name=httpd_proxy \
    --with-included-apr \
    --enable-mods-shared=all \
    --enable-ssl --enable-cgi --enable-proxy-connect --enable-file-cache --enable-proxy-ftp \
    --enable-proxy-ajp --enable-proxy-scgi\
    --enable-authn-file=static --enable-authn-default=static --enable-authz-host=static \
    --enable-authz-user=static --enable-authz-default=static --enable-auth-basic=static \
    --enable-status=static --enable-mime=static --enable-log-config=static \
    --enable-alias=static --enable-expires=static --enable-env=static --enable-deflate=static \
    --enable-proxy=static --enable-proxy-http=static --enable-proxy-balancer=static \
    --enable-cache=static --enable-disk-cache=static --enable-mem-cache=static \
    --enable-reqtimeout=static --enable-filter=static --enable-expires=static \
    --enable-headers=static --enable-setenvif=static --enable-version=static --enable-usertrack=static \
    --enable-vhost-alias=static --enable-dir=static --enable-alias=static --enable-rewrite=static \
    --with-module=bumpy_life_module:./mod_bumpy_life.c,cidr_lookup_module:./mod_cidr_lookup-1.2/apache2/mod_cidr_lookup.c,extract_forwarded_module:./extract_forwarded/mod_extract_forwarded.c
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

rm -rf $RPM_BUILD_ROOT%{prefix}/conf/extra/
rm -rf $RPM_BUILD_ROOT%{prefix}/conf/httpd_proxy.conf
rm -rf $RPM_BUILD_ROOT%{prefix}/htdocs/index.html
rm -rf $RPM_BUILD_ROOT%{prefix}/manual/
rm -rf $RPM_BUILD_ROOT%{prefix}/cgi-bin

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/httpd_proxy
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/httpd_proxy

install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{prefix}/htdocs/index.html
install -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{prefix}/htdocs/live.html

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/init.d
install -m 755 %{SOURCE5} \
   $RPM_BUILD_ROOT%{_sysconfdir}/init.d/httpd_proxy

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE6} \
   $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/httpd_proxy

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE9} \
   $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/httpd_proxy

install -m 644 %{SOURCE4} \
   $RPM_BUILD_ROOT%{prefix}/conf/httpd_proxy.conf

openssl genrsa -out sample.key 1024
openssl req -batch -new -key sample.key -out sample.csr
openssl req -x509 -in sample.csr -text -key sample.key  -out sample.crt
install -m 644 sample.key $RPM_BUILD_ROOT%{prefix}/conf/sample.key
install -m 644 sample.crt $RPM_BUILD_ROOT%{prefix}/conf/sample.crt

%pre
# Add the "www" user
/usr/sbin/groupadd -g 8001 www 2> /dev/null || :
/usr/sbin/useradd -c "WWW" -u 8001 -g 8001 \
        -s /sbin/nologin -r -d %{prefix} www 2> /dev/null || :

%post
/sbin/chkconfig --add httpd_proxy

%preun
if [ $1 = 0 ]; then
        /sbin/service httpd_proxy stop > /dev/null 2>&1
        /sbin/chkconfig --del httpd_proxy
fi

%files
%defattr(-,root,root,-)
%dir %{prefix}/bin
%dir %{prefix}/build
%dir %{prefix}/conf
%dir %{prefix}/error
%dir %{prefix}/htdocs
%dir %{prefix}/icons
%dir %{prefix}/include
%dir %{prefix}/lib
%dir %{prefix}/man
%dir %{prefix}/modules
%{prefix}/bin/*
%{prefix}/build/*
%{prefix}/error/*
%{prefix}/icons/*
%{prefix}/include/*
%{prefix}/lib/*
%{prefix}/man/*
%{prefix}/modules/*
%config(noreplace) %{prefix}/conf/httpd_proxy.conf
%config(noreplace) %{prefix}/conf/magic
%config(noreplace) %{prefix}/conf/mime.types
%config %{prefix}/conf/sample.key
%config %{prefix}/conf/sample.crt
%config %{prefix}/conf/original/extra/*
%config %{prefix}/conf/original/httpd.conf
%config(noreplace) %{prefix}/htdocs/index.html
%config(noreplace) %{prefix}/htdocs/live.html
%config %{_sysconfdir}/init.d/httpd_proxy
%config(noreplace) %{_sysconfdir}/sysconfig/httpd_proxy
%config(noreplace) %{_sysconfdir}/logrotate.d/httpd_proxy
%attr(0755,root,root) %dir %{_localstatedir}/log/httpd_proxy
%attr(0755,www,www) %dir %{_localstatedir}/cache/httpd_proxy

%changelog



