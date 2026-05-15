const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_16x9";
pptx.author = "GPT-5.4";
pptx.company = "Trae";
pptx.subject = "pptx skill working principle";
pptx.title = "pptx Skill 工作原理";
pptx.lang = "zh-CN";

const theme = {
  navy: "0F172A",
  teal: "0F766E",
  cyan: "14B8A6",
  sky: "E0F2FE",
  ink: "111827",
  slate: "475569",
  line: "CBD5E1",
  soft: "F8FAFC",
  white: "FFFFFF",
  mint: "CCFBF1",
  amber: "F59E0B",
  amberSoft: "FEF3C7",
  rose: "BE185D",
  roseSoft: "FCE7F3",
  green: "166534",
  greenSoft: "DCFCE7",
};

const slideH = 5.625;

function addBg(slide, color) {
  slide.background = { color };
}

function addTitle(slide, eyebrow, title, subtitle, opts = {}) {
  const dark = opts.dark || false;
  const titleColor = dark ? theme.white : theme.ink;
  const subtitleColor = dark ? "D6E3F1" : theme.slate;

  slide.addText(eyebrow, {
    x: 0.6,
    y: 0.35,
    w: 3.4,
    h: 0.22,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11,
    bold: true,
    color: dark ? "8BDAF0" : theme.teal,
    charSpacing: 1.2,
  });

  slide.addText(title, {
    x: 0.6,
    y: 0.58,
    w: 8.6,
    h: 0.6,
    margin: 0,
    fontFace: "Trebuchet MS",
    fontSize: 28,
    bold: true,
    color: titleColor,
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.62,
      y: 1.1,
      w: 8.2,
      h: 0.44,
      margin: 0,
      fontFace: "Calibri",
      fontSize: 12,
      color: subtitleColor,
      breakLine: false,
    });
  }
}

function addFooter(slide, page, dark = false) {
  slide.addText(`pptx skill explainers  |  第 ${page} 页`, {
    x: 0.62,
    y: 5.18,
    w: 3.5,
    h: 0.15,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 8,
    color: dark ? "A8B7C8" : "94A3B8",
  });
}

function addCard(slide, { x, y, w, h, fill, title, body, accent, titleColor, bodyColor }) {
  slide.addShape(pptx.shapes.RECTANGLE, {
    x,
    y,
    w,
    h,
    fill: { color: fill || theme.white },
    line: { color: accent || theme.line, width: 1 },
    radius: 0.08,
    shadow: { type: "outer", color: "000000", blur: 2, offset: 1, angle: 45, opacity: 0.08 },
  });

  slide.addShape(pptx.shapes.RECTANGLE, {
    x,
    y,
    w: 0.08,
    h,
    fill: { color: accent || theme.cyan },
    line: { color: accent || theme.cyan, width: 0 },
  });

  slide.addText(title, {
    x: x + 0.2,
    y: y + 0.16,
    w: w - 0.32,
    h: 0.28,
    margin: 0,
    fontFace: "Trebuchet MS",
    fontSize: 16,
    bold: true,
    color: titleColor || theme.ink,
  });

  slide.addText(body, {
    x: x + 0.2,
    y: y + 0.52,
    w: w - 0.32,
    h: h - 0.66,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11.5,
    color: bodyColor || theme.slate,
    valign: "top",
  });
}

function addPill(slide, text, x, y, w, fill, color) {
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x,
    y,
    w,
    h: 0.34,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: fill, width: 0 },
  });
  slide.addText(text, {
    x,
    y: y + 0.05,
    w,
    h: 0.16,
    margin: 0,
    align: "center",
    fontFace: "Calibri",
    fontSize: 10,
    bold: true,
    color,
  });
}

function addStep(slide, { x, y, num, title, desc, color }) {
  slide.addShape(pptx.shapes.OVAL, {
    x,
    y,
    w: 0.42,
    h: 0.42,
    fill: { color },
    line: { color, width: 0 },
  });
  slide.addText(String(num), {
    x,
    y: y + 0.07,
    w: 0.42,
    h: 0.16,
    margin: 0,
    align: "center",
    fontFace: "Trebuchet MS",
    fontSize: 12,
    bold: true,
    color: theme.white,
  });
  slide.addText(title, {
    x: x + 0.55,
    y: y - 0.02,
    w: 1.95,
    h: 0.22,
    margin: 0,
    fontFace: "Trebuchet MS",
    fontSize: 14,
    bold: true,
    color: theme.ink,
  });
  slide.addText(desc, {
    x: x + 0.55,
    y: y + 0.22,
    w: 2.15,
    h: 0.44,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 10.5,
    color: theme.slate,
  });
}

function addConnector(slide, x1, y1, x2, y2, color) {
  slide.addShape(pptx.shapes.LINE, {
    x: x1,
    y: y1,
    w: x2 - x1,
    h: y2 - y1,
    line: { color, width: 1.6, beginArrowType: "none", endArrowType: "triangle" },
  });
}

function addCodeBlock(slide, x, y, w, h, title, code) {
  slide.addShape(pptx.shapes.RECTANGLE, {
    x,
    y,
    w,
    h,
    fill: { color: theme.navy },
    line: { color: theme.navy, width: 0 },
    radius: 0.08,
  });
  slide.addText(title, {
    x: x + 0.18,
    y: y + 0.14,
    w: w - 0.36,
    h: 0.2,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 10,
    bold: true,
    color: "7DD3FC",
  });
  slide.addText(code, {
    x: x + 0.18,
    y: y + 0.38,
    w: w - 0.36,
    h: h - 0.5,
    margin: 0,
    fontFace: "Courier New",
    fontSize: 10.5,
    color: theme.white,
    breakLine: false,
  });
}

// Slide 1
{
  const slide = pptx.addSlide();
  addBg(slide, theme.navy);

  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 5.85,
    y: 0,
    w: 4.15,
    h: slideH,
    fill: { color: "0B1220", transparency: 8 },
    line: { color: "0B1220", width: 0 },
  });

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 0.62,
    y: 0.55,
    w: 1.55,
    h: 0.34,
    rectRadius: 0.08,
    fill: { color: theme.cyan, transparency: 10 },
    line: { color: theme.cyan, width: 0 },
  });
  slide.addText("Skill Deep Dive", {
    x: 0.62,
    y: 0.64,
    w: 1.55,
    h: 0.14,
    margin: 0,
    align: "center",
    fontFace: "Calibri",
    fontSize: 10,
    bold: true,
    color: theme.white,
  });

  slide.addText("pptx Skill\n工作原理说明", {
    x: 0.62,
    y: 1.12,
    w: 4.8,
    h: 1.36,
    margin: 0,
    fontFace: "Trebuchet MS",
    fontSize: 24,
    bold: true,
    color: theme.white,
    fit: "shrink",
  });

  slide.addText("这不是一个单纯的“做 PPT”提示词，而是一套围绕 PPTX 文件处理的决策框架：\n先判断任务类型，再选择“从零生成”或“模板编辑”，最后进入强制 QA 闭环。", {
    x: 0.64,
    y: 2.72,
    w: 4.55,
    h: 0.94,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 13,
    color: "DCE7F5",
    fit: "shrink",
  });

  addPill(slide, "触发广", 0.66, 4.22, 0.92, theme.teal, theme.white);
  addPill(slide, "流程化", 1.71, 4.22, 0.98, theme.cyan, theme.white);
  addPill(slide, "可验证", 2.84, 4.22, 1.02, "0EA5A4", theme.white);

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 6.15,
    y: 0.82,
    w: 3.15,
    h: 1.1,
    rectRadius: 0.08,
    fill: { color: "132033" },
    line: { color: "1F3A5A", width: 1 },
  });
  slide.addText("输入", {
    x: 6.42,
    y: 1.03,
    w: 0.45,
    h: 0.18,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11,
    bold: true,
    color: "7DD3FC",
  });
  slide.addText("用户提到 slides / presentation / .pptx", {
    x: 6.42,
    y: 1.28,
    w: 2.45,
    h: 0.28,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11.5,
    color: theme.white,
  });

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 6.15,
    y: 2.2,
    w: 3.15,
    h: 1.22,
    rectRadius: 0.08,
    fill: { color: "132033" },
    line: { color: "1F3A5A", width: 1 },
  });
  slide.addText("路由", {
    x: 6.42,
    y: 2.42,
    w: 0.45,
    h: 0.18,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11,
    bold: true,
    color: "86EFAC",
  });
  slide.addText("读取 / 修改 / 合并 / 新建 / QA", {
    x: 6.42,
    y: 2.68,
    w: 2.3,
    h: 0.25,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11.5,
    color: theme.white,
  });
  slide.addText("本质上是“选择正确工作流”的分发器", {
    x: 6.42,
    y: 2.98,
    w: 2.35,
    h: 0.24,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 10.5,
    color: "C0D2E6",
  });

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 6.15,
    y: 3.72,
    w: 3.15,
    h: 1.05,
    rectRadius: 0.08,
    fill: { color: theme.cyan },
    line: { color: theme.cyan, width: 0 },
  });
  slide.addText("输出", {
    x: 6.42,
    y: 3.96,
    w: 0.45,
    h: 0.18,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11,
    bold: true,
    color: theme.navy,
  });
  slide.addText("一个可靠、可检查、可继续编辑的 PPTX 文件", {
    x: 6.42,
    y: 4.2,
    w: 2.38,
    h: 0.3,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11.5,
    color: theme.navy,
  });

  addConnector(slide, 7.72, 1.92, 7.72, 2.19, "4FD1C5");
  addConnector(slide, 7.72, 3.42, 7.72, 3.71, "4FD1C5");
  addFooter(slide, 1, true);
}

// Slide 2
{
  const slide = pptx.addSlide();
  addBg(slide, theme.soft);
  addTitle(slide, "01 触发机制", "什么时候一定要调用这个 skill？", "它的核心不是内容主题，而是“是否涉及 .pptx 文件或演示文稿操作”。");

  addCard(slide, {
    x: 0.62,
    y: 1.62,
    w: 2.78,
    h: 1.42,
    fill: theme.white,
    accent: theme.cyan,
    title: "强触发词",
    body: "只要用户说 deck、slides、presentation，或直接提到 .pptx 文件名，就应该切换到 pptx skill。",
  });
  addCard(slide, {
    x: 3.58,
    y: 1.62,
    w: 2.78,
    h: 1.42,
    fill: theme.white,
    accent: theme.teal,
    title: "覆盖任务",
    body: "读取、提取文本、更新旧稿、改模板、拼接拆分、添加 speaker notes，甚至只是“看看 PPT 内容”也算。",
  });
  addCard(slide, {
    x: 6.54,
    y: 1.62,
    w: 2.84,
    h: 1.42,
    fill: theme.white,
    accent: theme.amber,
    title: "关键判断",
    body: "不是问“用户想讲什么”，而是问“这个需求是否会触碰 PPTX 文件”。只要触碰，就要启用专门流程。",
  });

  slide.addText("可以把它理解为一个文件类型路由器", {
    x: 0.64,
    y: 3.42,
    w: 3.4,
    h: 0.22,
    margin: 0,
    fontFace: "Trebuchet MS",
    fontSize: 18,
    bold: true,
    color: theme.ink,
  });

  addStep(slide, {
    x: 0.74, y: 3.88, num: 1, title: "识别输入", desc: "看到 slides / deck / .pptx / presentation 等信号。", color: theme.cyan,
  });
  addStep(slide, {
    x: 3.28, y: 3.88, num: 2, title: "进入技能", desc: "优先读取 skill 说明，而不是直接凭经验生成文件。", color: theme.teal,
  });
  addStep(slide, {
    x: 5.85, y: 3.88, num: 3, title: "选工作流", desc: "根据任务属于读取、模板编辑还是从零创建，切到对应指南。", color: theme.amber,
  });

  addConnector(slide, 2.76, 4.08, 3.18, 4.08, theme.line);
  addConnector(slide, 5.34, 4.08, 5.76, 4.08, theme.line);
  addFooter(slide, 2, false);
}

// Slide 3
{
  const slide = pptx.addSlide();
  addBg(slide, "F9FCFD");
  addTitle(slide, "02 总体架构", "pptx skill 的核心工作原理", "它将 PPT 相关需求分成三类入口，再通过工具链把结果收束到 QA。");

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 3.3,
    y: 1.52,
    w: 3.38,
    h: 0.82,
    rectRadius: 0.08,
    fill: { color: theme.navy },
    line: { color: theme.navy, width: 0 },
  });
  slide.addText("用户需求: “我要读取 / 修改 / 生成 PPTX”", {
    x: 3.3,
    y: 1.78,
    w: 3.38,
    h: 0.18,
    margin: 0,
    align: "center",
    fontFace: "Trebuchet MS",
    fontSize: 15,
    bold: true,
    color: theme.white,
  });

  addCard(slide, {
    x: 0.64,
    y: 2.74,
    w: 2.68,
    h: 1.62,
    fill: theme.white,
    accent: theme.cyan,
    title: "入口 A: 读取与分析",
    body: "用 `markitdown` 提取文本，用 `thumbnail.py` 看布局，用 `unpack.py` 看底层 XML 结构。",
  });
  addCard(slide, {
    x: 3.66,
    y: 2.74,
    w: 2.68,
    h: 1.62,
    fill: theme.white,
    accent: theme.teal,
    title: "入口 B: 模板编辑",
    body: "先分析模板，再解包、增删改 slide XML、清理孤儿资源，最后 pack 回新的 PPTX。",
  });
  addCard(slide, {
    x: 6.68,
    y: 2.74,
    w: 2.68,
    h: 1.62,
    fill: theme.white,
    accent: theme.amber,
    title: "入口 C: 从零创建",
    body: "走 `PptxGenJS` 工作流，以脚本方式构建版式、文本、形状、图表与输出文件。",
  });

  addConnector(slide, 4.99, 2.34, 1.98, 2.73, "94A3B8");
  addConnector(slide, 4.99, 2.34, 5.0, 2.73, "94A3B8");
  addConnector(slide, 4.99, 2.34, 8.02, 2.73, "94A3B8");

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 2.1,
    y: 4.58,
    w: 5.8,
    h: 0.56,
    rectRadius: 0.08,
    fill: { color: theme.mint },
    line: { color: "99F6E4", width: 1 },
  });
  slide.addText("三条路径最终都会回到同一个原则: 内容正确 + 文件可打开 + 视觉可检查", {
    x: 2.1,
    y: 4.77,
    w: 5.8,
    h: 0.16,
    margin: 0,
    align: "center",
    fontFace: "Calibri",
    fontSize: 11.5,
    bold: true,
    color: theme.green,
  });
  addFooter(slide, 3, false);
}

// Slide 4
{
  const slide = pptx.addSlide();
  addBg(slide, theme.soft);
  addTitle(slide, "03 从零生成", "当没有现成模板时，skill 会走 PptxGenJS 路线", "重点不是“手工做幻灯片”，而是“用代码定义版式和输出文件”。");

  addCard(slide, {
    x: 0.62,
    y: 1.62,
    w: 3.18,
    h: 2.82,
    fill: theme.white,
    accent: theme.cyan,
    title: "执行逻辑",
    body: "1. `require(\"pptxgenjs\")`\n2. 新建 presentation 实例\n3. 逐页 addSlide()\n4. 用 addText / addShape / addImage / addChart 组织内容\n5. `writeFile()` 产出最终 `.pptx`",
  });

  addCodeBlock(
    slide,
    4.1,
    1.68,
    5.26,
    1.78,
    "最小可运行骨架",
    "const PptxGenJS = require(\"pptxgenjs\");\nconst pptx = new PptxGenJS();\npptx.layout = \"LAYOUT_16x9\";\nconst slide = pptx.addSlide();\nslide.addText(\"Hello\", { x: 0.6, y: 0.6 });\nawait pptx.writeFile({ fileName: \"demo.pptx\" });"
  );

  addCard(slide, {
    x: 4.1,
    y: 3.66,
    w: 2.48,
    h: 0.88,
    fill: theme.sky,
    accent: theme.cyan,
    title: "版式本质",
    body: "坐标单位是英寸，所有对象都是“显式摆放”。",
  });
  addCard(slide, {
    x: 6.88,
    y: 3.66,
    w: 2.48,
    h: 0.88,
    fill: theme.amberSoft,
    accent: theme.amber,
    title: "设计守则",
    body: "避免纯白+项目符号；每页都要有视觉元素和层次变化。",
  });

  slide.addText("为什么这种方式适合 skill？", {
    x: 0.64,
    y: 4.78,
    w: 2.86,
    h: 0.2,
    margin: 0,
    fontFace: "Trebuchet MS",
    fontSize: 16,
    bold: true,
    color: theme.ink,
  });
  slide.addText("因为它可编排、可复现、可批量生成，适合代理稳定地生成交付件。", {
    x: 0.64,
    y: 5.02,
    w: 4.25,
    h: 0.18,
    margin: 0,
    fontFace: "Calibri",
    fontSize: 11,
    color: theme.slate,
  });
  addFooter(slide, 4, false);
}

// Slide 5
{
  const slide = pptx.addSlide();
  addBg(slide, "FCFFFE");
  addTitle(slide, "04 模板编辑", "已有参考稿时，skill 走“解包 XML -> 编辑 -> 回打包”", "这条路径的重点是保留模板设计，只替换结构和内容。");

  addStep(slide, {
    x: 0.74, y: 1.82, num: 1, title: "Analyze", desc: "先用缩略图和文本提取理解模板布局与占位内容。", color: theme.cyan,
  });
  addStep(slide, {
    x: 0.74, y: 2.7, num: 2, title: "Unpack", desc: "把 `.pptx` 解包成 XML 和资源文件，便于精细修改。", color: theme.teal,
  });
  addStep(slide, {
    x: 0.74, y: 3.58, num: 3, title: "Manipulate", desc: "删页、复制页、调整顺序，先做结构变化。", color: theme.amber,
  });
  addStep(slide, {
    x: 5.15, y: 1.82, num: 4, title: "Edit XML", desc: "逐个 slide XML 替换文本、图表、图片和占位元素。", color: theme.rose,
  });
  addStep(slide, {
    x: 5.15, y: 2.7, num: 5, title: "Clean", desc: "移除孤儿关系、无用媒体和失效引用，保持包结构干净。", color: theme.green,
  });
  addStep(slide, {
    x: 5.15, y: 3.58, num: 6, title: "Pack", desc: "重新打包并校验，导出新的演示文稿文件。", color: theme.navy,
  });

  addConnector(slide, 3.08, 2.03, 4.94, 2.03, theme.line);
  addConnector(slide, 3.08, 2.91, 4.94, 2.91, theme.line);
  addConnector(slide, 3.08, 3.79, 4.94, 3.79, theme.line);

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 1.4,
    y: 4.62,
    w: 7.2,
    h: 0.44,
    rectRadius: 0.06,
    fill: { color: theme.roseSoft },
    line: { color: "F9A8D4", width: 1 },
  });
  slide.addText("关键思想: 不直接“手抄一个新 PPT”，而是在原模板结构上做外科手术式修改。", {
    x: 1.4,
    y: 4.77,
    w: 7.2,
    h: 0.14,
    margin: 0,
    align: "center",
    fontFace: "Calibri",
    fontSize: 11,
    bold: true,
    color: theme.rose,
  });
  addFooter(slide, 5, false);
}

// Slide 6
{
  const slide = pptx.addSlide();
  addBg(slide, theme.soft);
  addTitle(slide, "05 QA 与依赖", "skill 为什么强调检查，而不是只看生成是否成功？", "因为 PPTX 很容易出现“文件能打开，但内容错位、残留占位符、结构已损坏”的隐性问题。");

  addCard(slide, {
    x: 0.62,
    y: 1.66,
    w: 2.86,
    h: 1.72,
    fill: theme.white,
    accent: theme.cyan,
    title: "内容 QA",
    body: "用 `python -m markitdown output.pptx` 回读文本，确认页序、标题、占位符和内容都正确。",
  });
  addCard(slide, {
    x: 3.58,
    y: 1.66,
    w: 2.86,
    h: 1.72,
    fill: theme.white,
    accent: theme.teal,
    title: "视觉 QA",
    body: "推荐把 PPT 转成 PDF / 图片后逐页检查：看是否溢出、遮挡、低对比、错位和不均匀间距。",
  });
  addCard(slide, {
    x: 6.54,
    y: 1.66,
    w: 2.84,
    h: 1.72,
    fill: theme.white,
    accent: theme.amber,
    title: "依赖工具",
    body: "`PptxGenJS` 负责创建，`markitdown` 负责读取，`soffice` + `pdftoppm` 负责视觉导出。",
  });

  addCard(slide, {
    x: 0.62,
    y: 3.7,
    w: 4.18,
    h: 1.04,
    fill: theme.greenSoft,
    accent: theme.green,
    title: "常见坑",
    body: "颜色不要写成 `#FF0000`；不要用 unicode 子弹符号；不要复用会被库内部修改的配置对象。",
  });
  addCard(slide, {
    x: 5.04,
    y: 3.7,
    w: 4.34,
    h: 1.04,
    fill: theme.roseSoft,
    accent: theme.rose,
    title: "真正的完成标准",
    body: "不是“脚本跑完了”，而是“PPT 能打开、信息正确、版式过检、没有遗留占位文本”。",
  });

  addFooter(slide, 6, false);
}

// Slide 7
{
  const slide = pptx.addSlide();
  addBg(slide, theme.navy);
  addTitle(slide, "06 总结", "一句话理解 pptx skill", "它是一套围绕 PPTX 文件的专用操作系统：先识别任务，再选择工作流，最后强制验证结果。", { dark: true });

  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 0.62,
    y: 1.72,
    w: 8.76,
    h: 2.08,
    rectRadius: 0.08,
    fill: { color: "132033" },
    line: { color: "21415E", width: 1 },
  });

  slide.addText("识别触发词  ->  进入 skill 说明  ->  选择读取 / 模板编辑 / 从零生成  ->  QA 闭环", {
    x: 0.88,
    y: 2.08,
    w: 8.2,
    h: 0.26,
    margin: 0,
    align: "center",
    fontFace: "Trebuchet MS",
    fontSize: 16,
    bold: true,
    color: theme.white,
  });

  slide.addText("对外看，它像一个做 PPT 的技能；对内看，它更像一个 PPTX 任务编排器。", {
    x: 1.08,
    y: 2.68,
    w: 7.8,
    h: 0.26,
    margin: 0,
    align: "center",
    fontFace: "Calibri",
    fontSize: 14,
    color: "DCE7F5",
  });

  addPill(slide, "路由正确", 1.58, 4.22, 1.28, theme.cyan, theme.navy);
  addPill(slide, "工作流正确", 3.16, 4.22, 1.46, "2DD4BF", theme.navy);
  addPill(slide, "结果可验证", 4.94, 4.22, 1.46, "99F6E4", theme.navy);
  addPill(slide, "输出可交付", 6.72, 4.22, 1.44, theme.white, theme.navy);
  addFooter(slide, 7, true);
}

// Speaker notes are intentionally omitted to keep the file lightweight.
(async () => {
  await pptx.writeFile({
    fileName: "/Users/Fei/Dev/repos/feiGitHub/fei_skills_hub/artifacts/pptx-skill-explainer/pptx-skill-workflow-explainer.pptx",
  });
})();
