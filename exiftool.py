import exiftool

print(exiftool.ExifTool('exiftool.exe'))

'''
files = ["./bitonals/00000001.jp2"]
with exiftool.ExifTool() as et:
    metadata = et.get_metadata_batch(files)
for d in metadata:
    print("{:20.20} {:20.20}".format(d["SourceFile"],
                                     d["EXIF:DateTimeOriginal"]))
'''