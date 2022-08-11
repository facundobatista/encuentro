!define PRODUCT_NAME "Encuentro"
!define PRODUCT_VERSION "6.0"
!define PRODUCT_PUBLISHER "Facundo Batista"
!define PRODUCT_WEB_SITE "http://encuentro.taniquetil.com.ar/"

!include "MUI2.nsh"
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${PRODUCT_NAME}_Setup.exe"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"

!define MUI_ABORTWARNING
!define MUI_ICON "windows\imgs\encuentro.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "windows\imgs\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "windows\imgs\sidebar.bmp"
!insertmacro MUI_PAGE_WELCOME
!define MUI_LICENSEPAGE
!insertmacro MUI_PAGE_LICENSE "COPYING"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
LicenseData "COPYING"
DirText " "
ShowInstDetails show

Section "Main"
SetOutPath "$INSTDIR"
File /r "dist\__main__\"
CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\__main__.exe"
SectionEnd

!define MUI_FINISHPAGE_RUN "$INSTDIR\__main__.exe"
!define MUI_FINISHPAGE_LINK "Sitio web del proyecto"
!define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_WEB_SITE}"

; these two goes in the end
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "Spanish"
