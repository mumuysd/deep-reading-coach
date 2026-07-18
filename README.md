<sub>🌐 <b>中文</b> · <a href="README.en.md">English</a></sub>

<div align="center">

# Deep Reading Coach｜深度阅读与学习教练

> *「别急着总结。先证明这本书真的可读。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-deep--reading--coach-blueviolet)](skills/deep-reading-coach/SKILL.md)
[![CI](https://github.com/mumuysd/deep-reading-coach/actions/workflows/validate.yml/badge.svg)](https://github.com/mumuysd/deep-reading-coach/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**先验证文件、目录和正文是否可读，再依据原书证据建立结构、拆解论证，并通过一次一个问题帮助读者形成自己的判断。**

**可读性先于总结 · 原书证据先于外部补全 · 理解先于结论**

[三阶段](#三阶段阅读流程) · [快速开始](#快速开始) · [实际输出](#实际输出) · [能力与边界](#能力与边界) · [验证与测试](#验证与测试)

</div>

---

![Deep Reading Coach demo](assets/demo.gif)

<sub>可复现演示：文件检查 → 原书范围确认 → 暂定全书地图 → 一个思考问题。</sub>

## 为什么需要它

把一本书交给 Agent 很容易，确认 Agent **实际上读到了什么**却很难：PDF 可能是扫描件，EPUB 可能把封面、版权页和导航页混入正文，目录可能缺失，提取文本也可能乱码。

更隐蔽的问题是，Agent 还没核对原书，就用网络简介或已有印象补全作者观点。Deep Reading Coach 把顺序固定为：

```text
检查材料 → 声明证据范围 → 建立全书地图 → 拆解观点 → 互动检验理解
```

通过入口检查后，技能先依据你提供的书重建作者的论证；成功提取文本也不会被表述成“已经完整阅读”。

## 三阶段阅读流程

文件可读性检查是进入阅读的门槛，不计作一个阅读阶段。

| 阶段 | 目标 | 证据边界 | 典型产出 |
|---|---|---|---|
| 一、原书重建 | 在作者自己的问题框架内还原结构、概念、主张、证据与推理 | 只使用原书和用户笔记 | 全书地图、观点拆解、原书定位、待确认问题 |
| 二、批判核实 | 核查数据、研究和结论是否可靠、过时或存在争议 | 可使用外部资料，必须标记并引用 | 支持、冲突、过时、仍无法确认及其适用范围 |
| 三、整合迁移 | 形成读者自己的判断，并把知识迁移到新情境 | 区分作者、外部证据、综合分析和读者判断 | 跨章节模型、独立判断、应用条件、反例与重读目标 |

三个阶段不是固定套餐。新书默认从阶段一开始；只有核实、更新或比较需要外部证据时才进入阶段二；阶段一也可以直接进入阶段三。阶段三本身不会自动触发联网。全书地图、带读、笔记审阅和整书整合是互动模式，可以在不同阶段使用。

阶段进度按 `未开始 / 进行中 / 当前范围完成 / 受阻` 记录，并注明全书、章节、摘录或笔记范围；用户理解程度另行诊断。完成某一范围的证据工作，不等于完整阅读全书，也不等于读者已经掌握。

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
使用 $deep-reading-coach 先检查这本书的可读性，只依据原书建立简洁的全书地图，并问我一个关键问题。
```

第一次响应只包含：

1. 文件读取情况；
2. 书籍基本信息；
3. 暂定全书结构；
4. 作者试图回答的核心问题；
5. 建议优先阅读的章节；
6. 一个需要你先思考的问题。

### 3. 安装可选解析依赖

PDF 和 DOCX 解析需要额外的 Python 包：

```bash
python3 -m pip install "pypdf>=5.0" "python-docx>=1.1"
```

仓库贡献者也可以在仓库根目录运行 `python3 -m pip install -r requirements-optional.txt`。EPUB、TXT、Markdown 和 HTML 只使用 Python 标准库。技能会先运行依赖自检；缺少依赖时会明确报告，不会假装解析成功。

## 实际输出

输入：

```text
使用 $deep-reading-coach 第一次阅读这本书，先给我简洁的全书地图。
```

真实测试输出节选：

```text
1. 文件读取情况
目录：可读；正文：可读。实际检查了目录和全部 3 个正文单元。
当前依据：完整提取文本已检查；这不等于已经完成深入阅读。

3. 暂定的全书结构
【原书内容】第一章提出判断应区分观察、推断与价值选择。
【综合归纳】全书主线暂定为：先拆分判断的组成，再用反例检验推断。

6. 一个需要我先思考的问题
当你看到一个现象时，你会怎样分别写出其中的“观察”“推断”和“价值选择”？
```

完整回放见 [examples/first-whole-book-response.md](examples/first-whole-book-response.md)。测试书中故意放入一段要求 Agent 联网和执行命令的文字；技能将其视为原书内容，没有执行。

## 能做什么

| 阅读任务 | 交付物 |
|---|---|
| 多格式材料检查 | `inspection.json`、结构索引、带来源定位的正文 |
| 第一次阅读 | 六部分的暂定全书地图 |
| 观点分析 | 主张、问题、证据、推理、前提、边界与常见误解 |
| 笔记审阅 | 笔记优先导航、理解准确处、遗漏、原书定位和一个诊断问题 |
| 互动学习 | 教学轮一个主要问题，最多三轮提示后给最小必要解释；纯核实轮可直接收束 |
| 书籍价值判断 | 强弱证据、时代与样本限制、适用与不适用范围 |

常用触发方式：

- “第一次读这本书，先给我全书地图。”
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
| `【教学分析】` | 对概念、论证或理解偏差的解释 |
| `【书外补充】` | 阶段二为核实、更新或比较而引入并引用的外部资料 |
| `【无法确认】` | 当前文件不足以支持的判断 |

阶段一禁用外部资料。只有进入阶段二，核实数据是否过时、补充研究、比较同领域书籍或回应用户明确要求时，才会使用并标记书外资料。

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
| 学习互动 | 一次输出全部结论 | 每轮推进一个主要问题 |
| 内容安全 | 可能执行书内提示 | 把书内命令和链接视为不可信来源数据 |

## 安全边界

- 不把“成功提取全文”描述成“已经完整阅读”。
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

回归集覆盖六种支持格式，以及损坏 EPUB、异常压缩、空白章节、缺失封面、加密 PDF、疑似扫描 PDF、乱码文本、无标题文本和依赖预检。行为用例覆盖书内提示注入、首次全书地图、原书加笔记、只有笔记、阶段二有界核实、阶段三禁止自动联网、部分材料暂定整合及技术书籍转交边界。

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

*先验可读性，再谈作者说了什么；先还原论证，再形成自己的判断。*

</div>
