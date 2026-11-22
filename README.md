# 天启竞技场 合并版

Release 标题：**天启**

完整 APK 约 2.71 GiB，超过 GitHub Release 单个文件 2 GiB 的上限；同时 GitHub 不接受中文资源文件名，因此分卷文件命名为：

- `TianQi.part1`（1,900,000,000 字节）
- `TianQi.part2`（1,005,971,935 字节）

## 合并还原

Windows：

```bat
copy /b TianQi.part1 + TianQi.part2 天启.apk
```

Linux / macOS：

```bash
cat TianQi.part1 TianQi.part2 > 天启.apk
```

合并后 SHA-256：

```
4663ca0de0e3d097c0b3703ba01154db62466be5a86b21c217e19fc414031c46
```
