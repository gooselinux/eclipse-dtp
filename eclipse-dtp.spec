%if 0%{?rhel} >= 6
%global debug_package %{nil}
%endif

%global eclipse_base     %{_libdir}/eclipse
%global eclipse_dropin   %{_datadir}/eclipse/dropins

Name:      eclipse-dtp
Version:   1.7.2
Release:   1%{?dist}
Summary:   Eclipse Data Tools Platform
Group:     System Environment/Libraries
License:   EPL
URL:       http://www.eclipse.org/datatools/

# source tarball and the script used to generate it from upstream's source control
# script usage:
# $ sh get-dtp.sh
Source0:   dtp-%{version}.tar.gz
Source1:   get-dtp.sh

Patch0:    %{name}-java6.patch

# remove duplicate plugin from sqltools features (it's actually built in the
# connectivity feature)
Patch1:    %{name}-remove-duplicate-plugin.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?rhel} >= 6
ExclusiveArch: i686 x86_64
%else
BuildArch: noarch
%endif

BuildRequires:    java-devel 
BuildRequires:    jpackage-utils
BuildRequires:    eclipse-pde >= 1:3.4.2
BuildRequires:    eclipse-emf
BuildRequires:    eclipse-gef
BuildRequires:    wsdl4j >= 1.5.2-6.6
BuildRequires:    xerces-j2 >= 2.7.1-10.3
BuildRequires:    xml-commons-resolver >= 1.1-2.15
BuildRequires:    xalan-j2 >= 2.7.0-7.5
BuildRequires:    xml-commons-apis >= 1.3.04-1.4
BuildRequires:    lpg-java-compat = 1.1.0

Requires:         java 
Requires:         jpackage-utils
Requires:         eclipse-platform >= 1:3.4.2
Requires:         eclipse-emf
Requires:         eclipse-gef
Requires:         wsdl4j >= 1.5.2-6.6
Requires:         xerces-j2 >= 2.7.1-10.3
Requires:         xml-commons-resolver >= 1.1-2.15
Requires:         xalan-j2 >= 2.7.0-7.5
Requires:         xml-commons-apis >= 1.3.04-1.4
Requires:         lpg-java-compat = 1.1.0

%description
The Eclipse Data Tools Platform provides extensible frameworks and exemplary 
tools, enabling a diverse set of plug-in offerings specific to particular 
data-centric technologies and supported by the DTP ecosystem.

%prep
%setup -q -n dtp-%{version}

# apply patches
%patch0
%patch1

# make sure upstream hasn't sneaked in any jars we don't know about
JARS=""
for j in `find -name "*.jar"`; do
  if [ ! -L $j ]; then
    JARS="$JARS $j"
  fi
done
if [ ! -z "$JARS" ]; then
   echo "These jars should be deleted and symlinked to system jars: $JARS"
   exit 1
fi

mkdir orbitDeps
pushd orbitDeps
ln -s %{_javadir}/xerces-j2.jar org.apache.xerces_2.9.0.jar
ln -s %{_javadir}/xalan-j2-serializer.jar org.apache.xml.serializer_2.7.1.jar
ln -s %{_javadir}/xml-commons-resolver.jar org.apache.xml.resolver_1.2.0.jar
ln -s %{_javadir}/xml-commons-apis.jar javax.xml_1.3.4.jar
ln -s %{_javadir}/wsdl4j.jar javax.wsdl_1.5.0.jar
ln -s %{_javadir}/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

%build
# Note: Use date from the cvs tag as the context qualifier.
OPTIONS="-DjavacTarget=1.5 -DjavacSource=1.5 -DforceContextQualifier=v200909251451"

# build all features except for documentation and SDK features TODO: build everything
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.modelbase.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.connectivity.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.sqldevtools.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.enablement.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{eclipse_dropin}
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-modelbase build/rpmBuild/org.eclipse.datatools.modelbase.feature.zip
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-connectivity build/rpmBuild/org.eclipse.datatools.connectivity.feature.zip
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-sqldevtools build/rpmBuild/org.eclipse.datatools.sqldevtools.feature.zip
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-enablement build/rpmBuild/org.eclipse.datatools.enablement.feature.zip

# use system bundles
pushd %{buildroot}%{eclipse_dropin}/dtp-enablement/eclipse/plugins
rm org.apache.xerces_*.jar
ln -s ../../../../../java/xerces-j2.jar org.apache.xerces_2.9.0.jar
rm org.apache.xml.serializer_*.jar
ln -s ../../../../../java/xalan-j2-serializer.jar org.apache.xml.serializer_2.7.1.jar
rm org.apache.xml.resolver_*.jar
ln -s ../../../../../java/xml-commons-resolver.jar org.apache.xml.resolver_1.2.0.jar
rm javax.xml_*.jar
ln -s ../../../../../java/xml-commons-apis.jar javax.xml_1.3.4.jar
rm javax.wsdl_*.jar
ln -s ../../../../../java/wsdl4j.jar javax.wsdl_1.5.0.jar
popd
pushd %{buildroot}%{eclipse_dropin}/dtp-sqldevtools/eclipse/plugins
rm net.sourceforge.lpg.lpgjavaruntime_*.jar
ln -s ../../../../../java/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{eclipse_dropin}/dtp-modelbase
%{eclipse_dropin}/dtp-connectivity
%{eclipse_dropin}/dtp-sqldevtools
%{eclipse_dropin}/dtp-enablement
%doc org.eclipse.datatools.sdk-all.feature/rootfiles/*

%changelog
* Thu Mar 11 2010 Alexander Kurtakov <akurtako@redhat.com> 1.7.2-1
- Update to 1.7.2.

* Fri Feb 12 2010 Andrew Overholt <overholt@redhat.com> 1.7.1-3
- Don't build debuginfo if building arch-specific packages.

* Thu Jan 21 2010 Andrew Overholt <overholt@redhat.com> 1.7.1-2
- Make arch-specific (x86, x86_64).

* Tue Oct 27 2009 Alexander Kurtakov <akurtako@redhat.com> 1.7.1-1
- Update to 1.7.1.

* Sat Sep 19 2009 Mat Booth <fedora@matbooth.co.uk> - 1.7.0-5
- Re-enable jar repacking now that RHBZ #461854 has been resolved.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Mat Booth <fedora@matbooth.co.uk> 1.7.0-3
- Disable jar repacking because of a bug in redhat-rpm-config, see #461854.
- Update dependency on wsdl4j.

* Sun Jul 05 2009 Mat Booth <fedora@matbooth.co.uk> 1.7.0-2
- Build all features.
- Add dependency on LPG.

* Thu Jul 02 2009 Mat Booth <fedora@matbooth.co.uk> 1.7.0-1
- Update to 1.7.0 final release (Galileo).
- Get map files from CVS instead of maintaining our own.
- Require Eclipse 3.4.2.

* Wed May 27 2009 Alexander Kurtakov <akurtako@redhat.com> 1.7.0-0.1.RC2
- Update to 1.7.0 RC2.
- Use %%global.

* Mon Mar 23 2009 Alexander Kurtakov <akurtako@redhat.com> 1.6.2-2
- Rebuild to not ship p2 context.xml.

* Fri Feb 27 2009 Alexander Kurtakov <akurtako@redhat.com> 1.6.2-1
- Update to 1.6.2.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 13 2009 Alexander Kurtakov <akurtako@redhat.com> 1.6.1-3
- Add patch to fix build with java 6.

* Wed Feb 11 2009 Alexander Kurtakov <akurtako@redhat.com> 1.6.1-2
- Set rt.jar to the build.
- Do not own dropins folder.
- Added comments about builded features and fixes.

* Wed Feb 9 2009 Alexander Kurtakov <akurtako@redhat.com> 1.6.1-1
- Initial package.
