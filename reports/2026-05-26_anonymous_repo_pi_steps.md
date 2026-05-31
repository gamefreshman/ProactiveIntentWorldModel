# Anonymous Repo 上传状态与后续维护

Codex 已经完成 private GitHub repo 创建、push、anonymous.4open.science 提交，以及 Overleaf URL 替换。

- Anonymous URL: `https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`
- Source repo status: private GitHub repo, branch `main`, commit `3a3c623`
- Overleaf status: Data and Code Availability 已使用上面的 anonymous URL

下面保留为后续维护检查清单。

## 步骤 1: 检查清单

打开 `reports/anon_repo_manifest_20260526.md`, 确认:

- [x] 30 视频 x 3 帧 = 90 张真实视频帧
- [x] 30 行 `annotations.jsonl`
- [x] 代码清洗 grep 全部零结果
- [x] 总大小 < 80MB

## 已完成: 创建 GitHub Private Repo

在 GitHub 网站:

- 已新建 private repository
- repo 名字: `piwm-emnlp2026-anonymous`
- 未使用 GitHub 初始化文件；内容来自 `/tmp/piwm_anon_repo`

## 已完成: Push 代码

```bash
cd /tmp/piwm_anon_repo
git remote add origin <private-github-repo-url>
git branch -M main
git push -u origin main
```

## 已完成: 提交 anonymous.4open.science

生成的 anonymous URL:

`https://anonymous.4open.science/r/piwm-emnlp2026-anonymous-D692/`

## 已完成: 更新论文 URL

Overleaf `acl_latex.tex` 的 Data and Code Availability section 已替换为实际 anonymous URL，并已重新编译。

## 注意事项

- GitHub repo 必须保持 private 直到论文 accepted (camera-ready 时改 public)
- anonymous.4open.science 提供的 URL 在 review 期间稳定可访问
- 论文接受后, 你可以把 GitHub repo 改 public, camera-ready 论文里换成真实 URL
