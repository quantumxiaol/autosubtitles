# auto subtitles

通过[yt-dlp](https://github.com/yt-dlp/yt-dlp)下载youtube的视频，需要使用cookies。

使用[whisper](https://github.com/openai/whisper)进行字幕的获取。

使用qwen进行翻译。输出双语字幕。

可以用来进行烤肉。

一些视频有自己的黑话（上蹄铁、马儿跳等），

## Environment

python 3.10

使用可编辑的方式安装了whisper

    git clone 
    uv venv
    uv sync

    # ffmpeg
    ## ubuntu
    sudo apt install ffmpeg
    ## macos
    brew install ffmpeg

## device

使用cpu或者cuda，mps不支持稀疏张量的操作。

## Get cookies for youtube

可以使用符合要求的浏览器扩展来导出 Cookie，例如适用于 Chrome 的 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) 或适用于 Firefox 的 [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)。

cookie 文件必须是 Mozilla/Netscape 格式，并且 cookies 文件的第一行必须是`# HTTP Cookie File`或者`# Netscape HTTP Cookie File`，


## Result

[wisper的调用结果](./docs/result.md)
