minecraft_logs_analyzer.exe:
	pyinstaller --clean --icon=icon.ico --onefile --splash=splash.png minecraft_logs_analyzer.pyw
	mv dist/minecraft_logs_analyzer.exe minecraft_logs_analyzer.exe
	rmdir dist
	rm -rf build


minecraft_logs_analyzersmaller.exe:
	pyinstaller --clean --icon=icon.ico --onefile --upx-dir="./upx-3.96-win64" --splash=splash.png minecraft_logs_analyzer.pyw
	mv dist/minecraft_logs_analyzer.exe minecraft_logs_analyzer.exe
	rmdir dist
	rm -rf build

make install:
	pip install -r requirements.txt
	wget https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip
	unzip upx-3.96-win64
clean:
	rm minecraft_logs_analyzer.exe
