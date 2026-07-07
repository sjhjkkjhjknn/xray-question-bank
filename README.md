# X射线探伤题库

手机端静态题库项目。题面来自 PDF 截图，不使用 OCR 重排题干；答案来自 PDF 第四部分。

## 内容

- 407 道题
- 基础知识：169 题
- 法律法规：131 题
- 专业实务：107 题
- 单选/多选自动判分
- 错题库和练习记录保存在浏览器本地

## GitHub Pages 部署

推荐把 `xray-question-bank` 文件夹作为一个独立 GitHub 仓库的根目录上传。

需要提交的核心内容：

- `index.html`
- `styles.css`
- `app.js`
- `manifest.webmanifest`
- `sw.js`
- `.nojekyll`
- `.github/workflows/deploy-pages.yml`
- `assets/`
- `data/`

不要提交这些构建缓存或 Android 尝试目录：

- `node_modules/`
- `android/`
- `.gradle-cache/`
- `www/`

上传后，在 GitHub 仓库页面进入：

```text
Settings -> Pages -> Build and deployment -> Source
```

选择：

```text
GitHub Actions
```

然后推送到 `main` 或 `master` 分支，GitHub Actions 会自动发布。发布完成后，手机直接访问 GitHub Pages 网址即可，不需要电脑开机，也不需要同一 Wi-Fi。

## 本地预览

```powershell
python -m http.server 5173
```

浏览器访问：

```text
http://localhost:5173
```

## 重新生成题库

```powershell
python .\tools\build_bank.py
python -c "from pathlib import Path; root=Path('.'); data=(root/'data/questions.json').read_text(encoding='utf-8'); (root/'data/questions.js').write_text('window.QUESTION_BANK = '+data+';\\n', encoding='utf-8')"
```

生成后检查：

- `data/questions.json`
- `data/build-checks.json`
- `assets/questions/*.jpg`
