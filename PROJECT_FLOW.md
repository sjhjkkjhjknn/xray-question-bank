# 科研、生产及其他题库项目流程

## 1. 项目目标

将 `科研、生产及其他.pdf` 中的题目整理为一个手机可访问、可互动答题、可记录错题的题库应用。

本项目采用静态网页 / PWA 形式部署到 GitHub Pages。题目内容以 PDF 截图形式呈现，不通过 OCR 重排题干，避免文字识别错误和排版变形。

线上访问地址：

```text
https://sjhjkkjhjknn.github.io/xray-question-bank/
```

## 2. 项目形式选择

最终选择 GitHub Pages 静态网页，而不是 Android APK。

原因：

- 不需要后端服务器。
- 不需要电脑开机或连接同一 Wi-Fi。
- 手机浏览器可直接访问。
- 可添加到手机主屏幕，接近 App 使用体验。
- 后续更新只需推送 GitHub，Actions 自动部署。

曾尝试 APK 方案，但 Android 构建链、Gradle 下载和本地环境配置耗时较长，因此改为更轻量的 GitHub Pages。

## 3. 核心目录结构

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
├─ .github/
│  └─ workflows/
│     └─ deploy-pages.yml
├─ .nojekyll
├─ .gitignore
└─ README.md
```

## 4. 题库生成流程

### 4.1 输入文件

原始 PDF：

```text
C:\CB\4-My work\424冷阴极X射线源\5其他\省辐射安全考试\科研、生产及其他.pdf
```

题目来自 PDF 第一、第二部分，答案从第三部分答案区整理。

### 4.2 自动生成

使用脚本：

```text
tools/build_bank.py
```

脚本主要完成：

- 解析 PDF 文本层中的题号、章节和答案。
- 判断单选题 / 多选题。
- 根据题号位置裁切题目区域截图。
- 输出题目截图到 `assets/questions/`。
- 输出结构化题库数据到 `data/questions.json`。
- 输出检查结果到 `data/build-checks.json`。

重新生成题库时使用：

```powershell
python .\tools\build_bank.py
python -c "from pathlib import Path; root=Path('.'); data=(root/'data/questions.json').read_text(encoding='utf-8'); (root/'data/questions.js').write_text('window.QUESTION_BANK = '+data+';\n', encoding='utf-8')"
```

### 4.3 生成结果检查

重点检查：

```text
data/questions.json
data/questions.js
data/build-checks.json
assets/questions/*.jpg
```

理想状态下，`data/build-checks.json` 中应没有缺失答案、缺失图片或重复题号。

示例：

```json
{
  "missingAnswerIds": [],
  "missingImageIds": [],
  "duplicateIds": [],
  "review": []
}
```

## 5. 特殊截图处理：末尾题目选项不全

PDF 页面末尾的题目可能出现跨页或选项被截断的问题。此时单张题目截图会导致选项不全，需要将同一道题的上半部分和下半部分分别截取，再拼接成一张完整题图。

处理原则：

- 不使用 OCR 补文字。
- 保持题干和选项均来自 PDF 原始截图。
- 拼接后的图片仍放在 `assets/questions/` 中，并覆盖或替换对应题号的图片。
- 更新后检查手机端显示是否完整。

可采用的整理步骤：

1. 找到选项不全的题号。
2. 用 `inspect_pages.py` 或 PDF 渲染工具确认该题跨越的页面位置。
3. 分别截取题目上半部分和下半部分。
4. 将两张截图纵向拼接。
5. 用拼接后的完整图片替换对应的 `assets/questions/*.jpg`。
6. 重新打开题库检查该题选项是否完整。

示例命令，仅作为流程记录，按需调整文件名和路径，不必固定执行：

```powershell
magick `
  assets\questions\q419_part1.jpg `
  assets\questions\q419_part2.jpg `
  -append `
  assets\questions\q419.jpg
```

如果没有安装 ImageMagick，也可以用任意图片编辑器手动纵向拼接，只要最终图片文件名与 `questions.json` 中引用的路径一致即可。

## 6. 前端功能

当前题库支持：

- 全部题目练习。
- 随机练习。
- 错题练习。
- 单选 / 多选自动判题。
- 本地错题库。
- 本地答题记录。
- 总题数、已答数、错题数、正确率统计。
- 手机端自适应布局。
- PWA 缓存，可添加到手机主屏幕。

当前交互规则：

- 取消“提交”按钮。
- 单选题点击选项后立即判题。
- 多选题选中数量达到正确答案数量后自动判题。
- 回答正确后自动跳转下一题。
- 回答错误后停留当前题，显示正确答案，需要手动点击“下一题”。

## 7. 本地预览

在项目根目录运行：

```powershell
python -m http.server 5173
```

浏览器访问：

```text
http://localhost:5173
```

或：

```text
http://127.0.0.1:5173
```

## 8. GitHub Pages 部署

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

## 9. 更新发布流程

每次修改功能或题库后：

```powershell
git status
git add .
git commit -m "描述本次修改"
git push origin main
```

然后到 GitHub 仓库的 Actions 页面确认部署状态。

## 10. 手机端缓存处理

由于项目使用了 Service Worker，部分浏览器可能继续显示旧版本。

处理方式：

- 在旧版浏览器中连续刷新 2-3 次。
- 关闭标签页后重新打开。
- 清除该站点缓存：`sjhjkkjhjknn.github.io`。
- 如果已添加到主屏幕，删除旧图标后重新添加。

每次有明显功能更新时，应同步更新 `sw.js` 中的缓存版本号，例如：

```js
const CACHE_NAME = "xray-question-bank-v3";
```

## 11. 不建议提交的目录

以下目录属于构建缓存或 APK 尝试过程产生的内容，不建议提交到 GitHub：

```text
node_modules/
android/
.gradle-cache/
www/
```

这些内容已通过 `.gitignore` 排除。

## 12. 项目当前状态

当前项目已完成：

- PDF 题目截图整理。
- 答案结构化。
- 手机端互动答题。
- 错题库和统计功能。
- GitHub Pages 自动部署。
- 手机浏览器访问验证。
- 答对自动跳转、答错手动下一题的交互优化。
