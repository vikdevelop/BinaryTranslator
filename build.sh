#!/usr/bin/bash
echo "Downloading depency runtime and SDK"
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --system runtime/org.gnome.Platform/x86_64/44 runtime/org.gnome.Sdk/x86_64/44 -y > /dev/null 2>&1
echo "Building app with Flatpak builder"
git clone https://github.com/vikdevelop/BinaryTranslator /tmp/BinaryTranslator > /dev/null 2>&1
cd /tmp/BinaryTranslator
flatpak-builder build *.yaml --install --user > /dev/null 2>&1
cd
rm -rf /tmp/BinaryTranslator
echo "BinaryTranslator has been installed successfully! Try run the app from desktop or terminal command 'flatpak run io.github.vikdevelop.BinaryTranslator'"
