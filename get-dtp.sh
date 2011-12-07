#!/bin/bash
NAME="dtp"
VERSION=1.7.1
TAG="DTP_1_7_1_Release_200909040500"
MAPFILES='
org.eclipse.datatools.releng/maps/dtp-features.map
org.eclipse.datatools.modelbase/releng/org.eclipse.datatools.modelbase.releng/maps/modelbase-plugins.map
org.eclipse.datatools.connectivity/releng/org.eclipse.datatools.connectivity.releng/maps/connectivity-plugins.map
org.eclipse.datatools.sqltools/releng/org.eclipse.datatools.sqltools.releng/maps/sqldevtools-plugins.map
org.eclipse.datatools.enablement/releng/org.eclipse.datatools.enablement.releng/maps/enablement-plugins.map'

echo "Exporting from CVS..."
mkdir $NAME-$VERSION
pushd $NAME-$VERSION >/dev/null

for MAPFILE in $MAPFILES; do

TEMPMAPFILE=temp.map
cvs -d :pserver:anonymous@dev.eclipse.org:/cvsroot/datatools export -r $TAG $MAPFILE
dos2unix $MAPFILE
grep ^[a-z] $MAPFILE > $TEMPMAPFILE

gawk 'BEGIN {
	FS=","
}
{
if (NF <  4) {

	split($1, version, "=");
	split(version[1], directory, "@");
	cvsdir=split($2, dirName, ":");
	printf("cvs -d %s%s %s %s %s %s %s\n", ":pserver:anonymous@dev.eclipse.org:", dirName[cvsdir], "-q export -r", version[2], "-d", directory[2], directory[2]) | "/bin/bash";
}
else {

	split($1, version, "=");
	total=split($4, directory, "/");
	cvsdir=split($2, dirName, ":");
	printf("cvs -d %s%s %s %s %s %s %s\n", ":pserver:anonymous@dev.eclipse.org:", dirName[cvsdir], "-q export -r", version[2], "-d", directory[total], $4) | "/bin/bash";
}

}' $TEMPMAPFILE

rm $TEMPMAPFILE $MAPFILE

done

popd >/dev/null

echo "Creating tarball '$NAME-$VERSION.tar.gz'..."
tar -czf $NAME-$VERSION.tar.gz $NAME-$VERSION
