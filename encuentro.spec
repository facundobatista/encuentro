Name:		encuentro
Version: 	0.5	
Release:	7%{?dist}
Summary:	Content visualization of Encuentro	
License:	GPLv3	
URL:		http://encuentro.taniquetil.com.ar/	
Source0:	http://launchpad.net/encuentro/trunk/0.5/+download/encuentro-%{version}.tar.gz
BuildArch: 	noarch
BuildRequires: 	python2-devel
BuildRequires:  desktop-file-utils
Requires: 	python-mechanize
Requires: 	python-twisted
Requires: 	pygtk2
Requires:	pyxdg

%description
Welcome to the Encuentro visualization program!
This is a simple program to search, download and see the content 
of the Canal Encuentro. This program is strongly oriented to 
Spanish speaking people, as the content of Encuentro is only in Spanish.  
Notes regarding licenses:
- The content of Encuentro is not distributed at all, but downloaded 
personally by the user, please check here to see the licenses about 
that content: http://www.encuentro.gov.ar

%prep
%setup -qn %{name}-%{version}
sed -i '1d' encuentro/__init__.py

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files
%{_bindir}/encuentro
%{_datadir}/applications/encuentro.desktop
%{_datadir}/encuentro/
%doc AUTHORS AYUDA.txt COPYING LEEME.txt README.txt version.txt
%exclude %{_datadir}/apport/

%changelog
* Fri Apr 27 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5-7
- Removed apport dir

* Thu Apr 26 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5-6
- Added %%exclude 

* Wed Apr 25 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5-5
- Fixed %%files
- Added sed in %%prep
- Removed period in summary
- Removed Group tag
- Added flag -q into %%setup

* Wed Apr 25 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5-4
- Added desktop-file-validate 
- Separated %%build and %%install sections
- Added doc files 

* Wed Apr 25 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5-3
- Added python macro 

* Sat Apr 21 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5-2
- Removed Prefix, Packager and Vendor.
- Removed empty %%build
- Removed %%clean

* Mon Apr 09 2012 Adrian Alves <alvesadrian@fedoraproject.org> 0.5
- First build.
