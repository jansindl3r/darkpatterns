for file in ./*/*.pdf
do
    pdf2svg "$file" "${file%.pdf}.svg"
done