# 售货员标注 Excel 美化报告

5-act 自检：Greet / Elicit / Inform / Recommend / Hold。

## 结论

原来的两个带图 Excel 可以用，但不适合直接发给公司或真人售货员：45 列横向展开，图片显示尺寸约 128x72，表头没有分组，填写区和系统预填区混在一起，打开后需要大量横向滚动。

已生成两个不覆盖原文件的美化版：

- `data/official/annotation_pack_v2/annotation_template_three_annotators_with_images_polished.xlsx`
- `data/official/annotation_pack_general_probe_v1/annotation_template_three_annotators_with_images_polished.xlsx`

## 改动内容

- 图片显示尺寸从约 128x72 放大到 250x141。
- 数据行高度从 82 调整到 122，避免图片和文字挤在一起。
- 表头按功能分区上色：观察材料、标注员信息、状态判断、介入决策、话术、动作适合度、质量备注。
- 需要售货员填写的单元格统一浅黄色，预填信息保持浅灰/白底。
- 启用筛选，冻结到 `F2`，方便横向滚动时仍能看到样本 ID、图片和场景描述。
- 给 1-5 分、主动作、阶段、介入判断等关键表头加了提示注释。
- 保留原 sheet 名、原 45 个字段名、原数据校验下拉、原图片和原样本顺序，不改变后处理 schema。

## 可复用机制

新增脚本：

`scripts/beautify_annotation_workbook.py`

用法示例：

```bash
python3 scripts/beautify_annotation_workbook.py \
  data/official/annotation_pack_v2/annotation_template_three_annotators_with_images.xlsx \
  data/official/annotation_pack_v2/annotation_template_three_annotators_with_images_polished.xlsx
```

## 校验

- `scripts/beautify_annotation_workbook.py` 已通过 `py_compile`。
- 两个美化版均可用 `openpyxl` 正常打开，sheet 数、行列数、图片数与原文件一致。
- target 主标注包：31 行 x 45 列，90 张图片。
- general probe 包：21 行 x 45 列，60 张图片。

SHA256：

- target polished: `a85fef883deca0c84fa4276b2957e10cf75dbb27b06990f5ac8f622c080c3e3c`
- general polished: `d7cb961b8f54ba4e6052db37cd90a07887fdb089b163a533f6abe78541fce709`
