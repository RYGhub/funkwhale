#! /bin/bash
set -e
[ -z $1 ] && echo "Path to list file missing" && exit 1

echo "This will download tracks from zip archives listed in $1"

LIST_CONTENT=$(cat $1)
mkdir -p data/music
cd data/music

echo "Downloading files..."
echo "$LIST_CONTENT" | grep "^[^#;]" | xargs -n 1 curl -LO

echo "Unzipping archives..."
find . -name "*.zip" | while read filename; do
    dirname="${filename%.*}"
    mkdir $dirname
    unzip -o -d "$dirname" "$filename";
done;

echo "Done!"
