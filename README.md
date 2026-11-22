# 天启竞技场 合并版

APK 完整文件约 2.71 GiB，超过 GitHub Release 单个文件 2 GiB 的限制，因此按分卷上传。

## 文件
- `天启.part1`
- `天启.part2`

## 合并还原
Windows:

```bat
copy /b 天启.part1 + 天启.part2 天启.apk
```

Linux / macOS:

```bash
cat 天启.part1 天启.part2 > 天启.apk
```

合并后 SHA-256：

```
4663ca0de0e3d097c0b3703ba01154db62466be5a86b21c217e19fc414031c46
```
