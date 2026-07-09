# 科研、生产及其他题库

这是一个面向手机使用的“科研、生产及其他”辐射安全考核题库。题目来自 PDF 原始截图，不使用 OCR 重排题干；答案来自 PDF 第三部分答案区。

在线访问：

```text
https://sjhjkkjhjknn.github.io/xray-question-bank/
```

## 当前功能

- 419 道题目。
- 支持全部练习、随机练习、错题练习。
- 支持单选题和多选题。
- 题目以 PDF 截图显示，尽量保持原卷版式。
- 自动判题。
- 答对后自动跳转下一题。
- 答错后停留当前题，显示正确答案，需要手动点击“下一题”。
- 自动记录已答题目、错题数和正确率。
- 错题库和答题记录保存在当前浏览器本地。
- 可在手机浏览器中访问，也可添加到手机主屏幕。

## 项目结构

```text
xray-question-bank/
├─ index.html
├─ styles.css
├─ app.js
├─ manifest.webmanifest
├─ sw.js
├─ data/
│  ├─ questions.json
│  ├─ questions.js
│  └─ build-checks.json
├─ assets/
│  ├─ icon.svg
│  └─ questions/
│     └─ *.jpg
├─ tools/
│  ├─ build_bank.py
│  └─ inspect_pages.py
├─ .github/workflows/deploy-pages.yml
├─ PROJECT_FLOW.md
└─ README.md
```

## 手机使用

直接在手机浏览器打开：

```text
https://sjhjkkjhjknn.github.io/xray-question-bank/
```

如果希望像 App 一样使用，可以在手机浏览器中选择“添加到主屏幕”。

如果一个浏览器已经是新版，另一个浏览器仍是旧版，通常是缓存导致的。可以连续刷新 2-3 次，或清除 `sjhjkkjhjknn.github.io` 的站点缓存后重新打开。

## 本地预览

在项目根目录运行：

```powershell
python -m http.server 5173
```

然后访问：

```text
http://localhost:5173
```

或：

```text
http://127.0.0.1:5173
```

## 重新生成题库

题库生成脚本位于：

```text
tools/build_bank.py
```

重新从 PDF 生成截图和题库数据：

```powershell
python .\tools\build_bank.py
python -c "from pathlib import Path; root=Path('.'); data=(root/'data/questions.json').read_text(encoding='utf-8'); (root/'data/questions.js').write_text('window.QUESTION_BANK = '+data+';\n', encoding='utf-8')"
```

生成后重点检查：

```text
data/questions.json
data/questions.js
data/build-checks.json
assets/questions/*.jpg
```

## 特殊情况：题目截图不完整

PDF 页面末尾的题目可能跨页，导致单张截图中选项不全。处理方式是分别截取该题的上半部分和下半部分，再纵向拼接成一张完整图片，替换对应的 `assets/questions/*.jpg`。

示例命令仅作流程记录，按实际题号和文件名调整：

```powershell
magick `
  assets\questions\q419_part1.jpg `
  assets\questions\q419_part2.jpg `
  -append `
  assets\questions\q419.jpg
```

没有 ImageMagick 时，也可以用图片编辑器手动拼接。最终文件名需要和 `data/questions.json` 中引用的图片路径一致。

## GitHub Pages 部署

仓库地址：

```text
https://github.com/sjhjkkjhjknn/xray-question-bank
```

部署方式：

```text
Settings -> Pages -> Build and deployment -> Source -> GitHub Actions
```

工作流文件：

```text
.github/workflows/deploy-pages.yml
```

推送到 `main` 分支后，GitHub Actions 会自动部署。部署成功后，Actions 页面中的 `Deploy GitHub Pages` 应显示绿色对勾。

## 更新发布

修改代码、题库或文档后：

```powershell
git status
git add .
git commit -m "描述本次修改"
git push origin main
```

推送后等待 GitHub Actions 部署完成，再刷新手机页面。

## 缓存版本

本项目使用 Service Worker 做离线缓存。功能更新后，应同步更新 `sw.js` 中的缓存名，例如：

```js
const CACHE_NAME = "xray-question-bank-v3";
```

这样可以减少手机浏览器继续显示旧版本的情况。

## 不提交的目录

以下目录是依赖、构建缓存或 APK 尝试过程产生的内容，不建议提交到 GitHub：

```text
node_modules/
android/
.gradle-cache/
www/
```

这些目录已在 `.gitignore` 中排除。

## 详细流程

完整项目过程、技术选择、截图生成、部署排错和维护说明见：

```text
PROJECT_FLOW.md
```
