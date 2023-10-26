#!/bin/bash

#LOG INTO ISSDC MANUALLY
#FIREFOX: ctrl+shift+I > Storage > Cookies > Value for JSESSIONID (/ch2)
#CHROME: ctrl+shift+I > Application > Storage > Cookies > Value for JSESSIONID (/ch2)
#COPY THE value IN THE NEXT LINE

cookies="JSESSIONID=17c9ef39cc845336bbf1c5bfd9c1"


# Read filenames from "filenames.txt" and store them in the array
readarray -t filenames < "filenames.txt"


function get_data_file_paths() {
    local filenames=("$@")
    local dataFilePaths=()

    for filename in "${filenames[@]}"; do
        # Get the directory of the filename.
        local directory="/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/cla_collection/cla/data/calibrated/${filename:11:4}/${filename:15:2}/${filename:17:2}"

        # Get the full data file path.
        local dataFilePath="${directory}/${filename}?class"

        # Check if the file already exists.
        if [[ -f "class_data/$filename" ]]; then
            # File already exists, skip it.
            continue
        fi

        # Add the data file path to the array.
        dataFilePaths+=("$dataFilePath")
    done

    # Print the data file paths 
    for path in "${dataFilePaths[@]}"; do
        echo "$path"
    done

}


urlPrefix="https://pradan.issdc.gov.in"
proxyOptions=""

# Check if the directory "class" exists
if [ ! -d "class_data" ]; then
    # Create the directory if it does not exist
    echo "Created class_data directory"
    mkdir "class_data"
fi

# filenames=("ch2_cla_l1_20230513T163233607_20230513T163241607.fits" "ch2_cla_l1_20230513T163225607_20230513T163233607.fits" "ch2_cla_l1_20230513T162105607_20230513T162113607.fits")

dataFilePaths1=($(get_data_file_paths "${filenames[@]}"))
echo "Preparing links to download..."
dataFilePaths=("/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/cla_collection/cla/data/calibrated/2023/05/13/ch2_cla_l1_20230513T163233607_20230513T163241607.fits?class" "/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/cla_collection/cla/data/calibrated/2023/05/13/ch2_cla_l1_20230513T163225607_20230513T163233607.fits?class" )

total_files=${#dataFilePaths1[@]}
i=0;

for file in ${dataFilePaths1[@]}
do 
	#echo $file; 
	i=$(($i+1));
	progress="$i/$total_files"

	# Display the progress
	echo -ne "Downloading $filename ($progress)...\r"

	wget $proxyOptions -q --content-disposition --tries=1 --no-cookies --max-redirect=0 --header "Cookie: $cookies" $urlPrefix$file -P class_data;

	# Check the exit status of the wget command
    if [ $? -ne 0 ]; then
    	echo 
	echo "Got some error downloading file $i: ${file:121:53}"
	echo "You may login again later to download the script for the new session and resume downloads"
        echo 
        exit -1
    fi

done

echo "Your ($i) downloads are complete."
