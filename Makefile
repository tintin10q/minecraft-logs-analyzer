minecraft_logs_analyzer.exe:
	pyinstaller --clean --icon=icon.ico --onefile --splash=splash.png minecraft_logs_analyzer.pyw
	mv dist/minecraft_logs_analyzer.exe minecraft_logs_analyzer.exe
	rmdir dist
	rm -rf build


minecraft_logs_analyzersmaller.exe:
	pyinstaller --clean --icon=icon.ico --onefile --upx-dir="./upx-4.2.4-win64" --splash=splash.png minecraft_logs_analyzer.pyw
	mv dist/minecraft_logs_analyzer.exe minecraft_logs_analyzer.exe
	rmdir dist
	rm -rf build


make install:
	pip install -r requirements.txt
	wget https://github.com/upx/upx/releases/download/v4.2.4/upx-4.2.4-win64.zip
	unzip upx-4.2.4-win64

clean:
	rm -f minecraft_logs_analyzer.exe
	rm -f minecraft_logs_analyzer.spec
	rm -fr dist
	rm -fr build
