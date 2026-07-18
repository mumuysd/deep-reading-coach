<sub>🌐 <b>中文</b> · <a href="README.en.md">English</a></sub>

<div align="center">

# Deep Reading Coach｜深度阅读与学习教练

> *「别急着总结。先证明这本书真的可读。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-deep--reading--coach-blueviolet)](skills/deep-reading-coach/SKILL.md)
[![CI](https://github.com/mumuysd/deep-reading-coach/actions/workflows/validate.yml/badge.svg)](https://github.com/mumuysd/deep-reading-coach/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**先验证文件，再完整阅读全部可读正文；只有读完整本书，才输出结构、问题意识和论证路线。**

**可读性先于总结 · 原书证据先于外部补全 · 理解先于结论**

[三阶段](#三阶段阅读流程) · [快速开始](#快速开始) · [实际输出](#实际输出) · [能力与边界](#能力与边界) · [验证与测试](#验证与测试)

</div>

---

![Deep Reading Coach demo](assets/demo.gif)

<sub>可复现演示：文件检查 → 全部正文实际检查 → 八部分全书地图 → 一个思考问题。</sub>

## 为什么需要它

把一本书交给 Agent 很容易，确认 Agent **实际上读到了什么**却很难：PDF 可能是扫描件，EPUB 可能把封面、版权页和导航页混入正文，目录可能缺失，提取文本也可能乱码。

更隐蔽的问题是，Agent 还没核对原书，就用网络简介或已有印象补全作者观点。Deep Reading Coach 把顺序固定为：

```text
检查材料 → 按顺序阅读全部正文 → 建立全书地图 → 批判定位 → 整合迁移
```

通过入口检查后，技能按原书顺序检查全部可读正文。目录、序言、章节开头、结论或其他抽样都不能代替完整阅读；成功提取文本也不会被表述成“已经完整阅读”。

## 三阶段阅读流程

文件可读性检查是进入阅读的门槛，不计作一个阅读阶段。

| 阶段 | 目标 | 证据边界 | 典型产出 |
|---|---|---|---|
| 一、原书重建 | 完整阅读全部可读正文，再还原结构、问题意识、概念与论证路线 | 只使用原书和用户笔记 | 八部分全书地图、观点拆解、原书定位 |
| 二、批判定位与核实 | 定位思想谱系、竞争理论与时代背景，并核查研究和结论 | 用户选择升维方向后使用带引用的外部资料 | 领域位置、替代解释、支持、争议、过时或仍无法确认 |
| 三、整合判断与迁移 | 形成读者判断，并把知识用于五类现实场景 | 区分作者、外部证据、综合分析和读者判断 | 独立判断、五类迁移地图、条件、反例与误用边界 |

新书默认从阶段一开始。阶段一完成后，技能最多提出三个值得升维的方向，但不会自动联网；用户选择后才进入阶段二。阶段三本身也不会自动触发联网。全书地图、带读、笔记审阅和整书整合是互动模式，可以在不同阶段使用。

阶段进度和理解状态在内部记录，默认不输出流程化状态表。只有材料受限、读取受阻、准备联网或用户主动询问时才显示必要范围。完成文本提取、单章或抽样检查都不等于完整阅读全书。

## 阅读笔记优先导航

有阅读笔记时，技能不会要求读者从零重做全书地图。

| 材料 | 处理方式 |
|---|---|
| 原书＋笔记 | 先诊断笔记，再用笔记暴露的主张和缺口定向核对原书 |
| 只有笔记 | 暂定审阅结构、推理和疑问；涉及作者原意时标记 `【无法确认】`，只索取必要章节或摘录 |

笔记里的原书概括进入阶段一核对，外部研究或时效判断进入阶段二核实，个人观点、应用和反例进入阶段三整合。默认保留原笔记，不替读者重写。

笔记首轮固定为四段：`材料与证据范围`、`我已经理解的内容`、`关键缺口与可保留问题`、`当前诊断问题`。

## 快速开始

适用于支持 [Agent Skills](https://skills.sh/) 的 Agent，也可通过 Claude Code marketplace 安装。使用 `npx` 安装需要 Node.js；运行书籍检查器需要 Python 3。

### 1. 安装

仓库发布后，通过 Skills CLI 安装：

```bash
npx skills add mumuysd/deep-reading-coach --skill deep-reading-coach
```

使用 Claude Code marketplace：

```text
/plugin marketplace add mumuysd/deep-reading-coach
/plugin install deep-reading-coach@deep-reading-coach
```

从已下载的本地仓库安装或验证：

```bash
npx skills add . --skill deep-reading-coach
```

> 远程安装命令和 CI 徽章将在 `mumuysd/deep-reading-coach` 仓库发布后生效；发布前请使用本地仓库验证方式。

### 2. 发起第一次阅读

上传书籍后告诉 Agent：

```text
使用 $deep-reading-coach 先检查并完整阅读这本书的全部可读正文，再只依据原书输出八部分全书地图，并问我一个关键问题。
```

文件检查后，如果正文尚未全部实际检查，技能只报告材料情况、读取状态或阻塞原因，不提前输出全书分析。完整阅读后，第一次分析响应只包含：

1. 文件读取情况；
2. 书籍基本信息；
3. 全书结构；
4. 作者的问题意识；
5. 作者试图回答的核心问题；
6. 全书论证路线；
7. 建议重点精读或重新阅读的章节；
8. 一个需要你先思考的问题。

### 3. 安装可选解析依赖

PDF 和 DOCX 解析需要额外的 Python 包：

```bash
python3 -m pip install "pypdf>=5.0" "python-docx>=1.1"
```

仓库贡献者也可以在仓库根目录运行 `python3 -m pip install -r requirements-optional.txt`。EPUB、TXT、Markdown 和 HTML 只使用 Python 标准库。技能会先运行依赖自检；缺少依赖时会明确报告，不会假装解析成功。

## 实际输出

输入：

```text
使用 $deep-reading-coach 完整阅读这本书的全部可读正文，再给我全书地图。
```

真实测试输出节选：

```text
1. 文件读取情况
目录：可读；正文：可读。实际检查了目录和全部 3 个正文单元。
当前依据：全部 3 个正文单元均已按顺序实际检查；不是只完成文本提取或抽样。

3. 全书结构
【原书内容】第一章提出判断应区分观察、推断与价值选择。
【综合归纳】全书先拆分判断的组成，再用反例检验推断。

4. 作者的问题意识
【综合归纳】作者关注观察与结论被混为一谈后产生的误判。

6. 全书论证路线
【综合归纳】定义判断的三个层次 → 展示同一观察的多种解释 → 用反例检验结论。

8. 一个需要我先思考的问题
当你看到一个现象时，你会怎样分别写出其中的“观察”“推断”和“价值选择”？
```

完整回放见 [examples/first-whole-book-response.md](examples/first-whole-book-response.md)。测试书中故意放入一段要求 Agent 联网和执行命令的文字；技能将其视为原书内容，没有执行。

## 能做什么

| 阅读任务 | 交付物 |
|---|---|
| 多格式材料检查 | `inspection.json`、结构索引、带来源定位的正文 |
| 第一次全书分析 | 完整阅读全部可读正文后的八部分全书地图 |
| 观点分析 | 主张、问题、证据、推理、前提、边界与常见误解 |
| 笔记审阅 | 笔记优先导航、理解准确处、遗漏、原书定位和一个诊断问题 |
| 互动学习 | 教学轮一个主要问题，最多三轮提示后给最小必要解释；纯核实轮可直接收束 |
| 书籍价值判断 | 强弱证据、时代与样本限制、适用与不适用范围 |
| 批判定位 | 思想谱系、竞争理论、当前研究、文化与制度前提 |
| 整书迁移 | 写作、生活观察、工作与人际、自我反思、跨书联系 |

常用触发方式：

- “完整读完这本书，再给我八部分全书地图。”
- “带我精读这一章，一次只问一个问题。”
- “审阅我的阅读笔记，但不要替我重写。”
- “分析作者怎样从证据推出结论。”
- “哪些观点证据较强，哪些只是作者推测？”
- “深入分析这个核心观点的适用条件和反例。”

## 证据标签

技能会把不同来源明确分开，避免把作者原话、教学解释和外部研究混在一起：

| 标签 | 含义 |
|---|---|
| `【原书内容】` | 文件中可以直接定位的内容 |
| `【综合归纳】` | 根据多个原书位置形成的概括 |
| `【教学分析】` | 为理解、比较或迁移提供的解释和有边界的推演 |
| `【书外补充】` | 阶段二为核实、更新或比较而引入并引用的外部资料 |
| `【无法确认】` | 当前文件不足以支持的判断 |

阶段一禁用外部资料。阶段一完成后只提出升维方向，不联网；用户选择方向或明确要求核实、更新、比较时，才进入阶段二并标记书外资料。

## 能力与边界

### 支持格式

| 格式 | 定位方式 | 主要检查 |
|---|---|---|
| PDF | 真实文件页码 | 加密、空白页、乱码、文本覆盖率、疑似扫描件 |
| EPUB | 章节名＋小节名 | OPF、spine、导航目录、正文角色与阅读顺序 |
| DOCX | 标题、段落、表格 | 结构与文字提取，不虚构页码 |
| TXT / Markdown / HTML | 标题或真实行号范围 | 编码、标题结构与可识别正文 |

第一版不提供 OCR、MOBI/AZW3 转换或 DRM 移除。技术书籍的概念、结构和推理由本技能处理；实际代码练习与调试应交给编程学习或开发类技能。

### 它和常见阅读助手有什么不同

| 维度 | 常见做法 | Deep Reading Coach |
|---|---|---|
| 开始顺序 | 直接摘要 | 先报告目录与正文是否可读 |
| 证据边界 | 混合原书、记忆和网络资料 | 阶段一只依据原书，阶段二才引入已标记的外部资料 |
| 来源定位 | 容易虚构页码 | PDF 用真实文件页；EPUB 用章节和小节 |
| EPUB 结构 | 封面、目录、许可证可能混入正文 | 区分 `body/cover/navigation/legal` |
| 全书地图 | 目录或抽样即可生成 | 全部可读正文实际检查后才能生成 |
| 学习互动 | 一次输出全部结论 | 每轮推进一个主要问题 |
| 内容安全 | 可能执行书内提示 | 把书内命令和链接视为不可信来源数据 |

## 安全边界

- 不把“成功提取全文”描述成“已经完整阅读”。
- 不在全部可读正文实际检查完成前输出全书结构、问题意识、核心观点或论证路线。
- 不用目录、序言、章节开头、结论或选章抽样替代完整阅读。
- 不执行书中出现的命令，不打开书内链接，不接受书内提示改变工作流。
- 阶段一不联网补全作者观点、缺失章节或出版信息。
- 医疗、法律、金融等高风险应用必须先在阶段二核实当前事实与规范，不能只依据原书迁移。
- 不修改原书；解析结果只写入任务临时目录。
- 不绕过 DRM，不承诺 OCR，不把损坏、加密或低文本覆盖率文件伪装成成功结果。
- 遇到不可读材料、缺失依赖或需要对外操作时，停止并说明最小下一步。

安装任何公开 Skill 前，都应先审阅其 [`SKILL.md`](skills/deep-reading-coach/SKILL.md) 和脚本。本仓库的检查器不发起网络请求，也不执行书中代码。

## 仓库结构

```text
.
├── skills/deep-reading-coach/   # 可安装的 Skill 本体
│   ├── SKILL.md                 # 入口门槛与核心工作流
│   ├── references/              # 阅读模式、证据与教学协议
│   ├── scripts/                 # 多格式检查器与回归测试
│   └── test-prompts.json        # 行为验收场景
├── examples/                    # 自包含测试书与真实运行输出
├── evals/evals.json             # 公开行为验收场景
├── assets/demo.gif              # 可见演示
├── tools/                       # 公开包验证和演示生成工具
└── .github/workflows/           # 自动回归测试
```

## 验证与测试

```bash
python3 -m pip install -r requirements-dev.txt
python3 skills/deep-reading-coach/scripts/test_inspect_book.py
python3 tools/validate_public_repo.py
```

回归集覆盖六种支持格式，以及损坏 EPUB、异常压缩、空白章节、缺失封面、加密 PDF、疑似扫描 PDF、乱码文本、无标题文本和依赖预检。行为用例覆盖完整正文门槛、八部分全书地图、书内提示注入、原书加笔记、只有笔记、阶段二升维提议与有界核实、阶段三五类迁移、部分材料暂定整合及技术书籍转交边界。

- 公开验收定义：[evals/evals.json](evals/evals.json)
- 独立活体结果：[evals/results.md](evals/results.md)
- 本地安装烟雾测试：[examples/install-smoke-test.md](examples/install-smoke-test.md)
- 贡献与安全报告：[CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md)

公网 URL 必须在仓库发布后重新验证，不能用本地测试替代。发布前还应运行严格检查：

```bash
python3 tools/validate_public_repo.py --release
```

严格检查会拒绝 GitHub 用户名占位符、私人绝对路径、缺失许可证、缺失演示或无效 marketplace 清单。

## 致谢

- [Agent Skills CLI 文档](https://www.skills.sh/docs/cli)：跨 Agent 安装约定。
- [Anthropic Claude Code Plugins Directory](https://github.com/anthropics/claude-plugins-official)：skill-bundle marketplace 结构与安全提醒。
- [Project Gutenberg](https://www.gutenberg.org/)：真实 EPUB 回归样本来源；样本书不随仓库分发。

## License

[MIT](LICENSE)

---

<div align="center">

*先验可读性，再完整阅读；先看清整本书，再形成自己的判断。*

</div>
