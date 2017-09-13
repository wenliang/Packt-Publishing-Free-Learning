@echo off
cd %0\..
if "%1" == "-l" (
    echo ***Date: %DATE:/=-% [%TIME::=:%] *** >> packtPublishingFreeEbook.log
    echo *** Grabbing free eBook from Packt Publishing.... *** >> packtPublishingFreeEbook.log
    python packtPublishingFreeEbook.py -da >> packtPublishingFreeEbook.log 2>&1
    echo:
    echo:>> packtPublishingFreeEbook.log
) ELSE (
    echo *** Grabbing free eBook from Packt Publishing.... ***
    python packtPublishingFreeEbook.py -da
    echo *** Done ! ***
)
pause
if "%1" == "-p" (
    pause
)
if "%2" == "-p" (
    pause
)
