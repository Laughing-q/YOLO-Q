# YOLO🚀
🔥🔥🔥A inference framework that support multi models of `yolo5`(torch and tensorrt), `yolox`(torch and tensorrt), 
`nanodet`(tensorrt), `yolo-fastestV2`(tensorrt) and `yolov5-lite`(tensorrt).

<p align="center"> <img src='assert/teaser.jpg' align="center"> </p>

## Support
- [X] yolov5(torch, tensorrtx, tensorrt)
- [X] yolox(torch, tensorrt)
- [X] yolov5-lite(tensorrt)
- [X] nanodet(tensorrt)

## TODO
- [X] same interface of `yolov5` and `yolox`.
- [X] **add time**
- [ ] better multi-threading
- [ ] add Counter
- [ ] add log
- [X] add `save` function in data reader.
- [ ] return the output with dict type
- [ ] device
- [ ] add `yolov5-q`
- [ ] model half and image half

<!-- ## <div align="center">Quick Start</div> -->
## Quick Start

<details open>
<summary>Installation</summary>

Clone repo and install [requirements.txt](https://github.com/Laughing-q/YOLO-Q/blob/master/requirements.txt) in a
**Python>=3.7.0** environment, including
**PyTorch>=1.7.1** and **Tensorrt >= 8.2.1.8**.

```shell
pip install git+https://github.com/Laughing-q/yolov5-q.git
pip install git+https://github.com/Laughing-q/lqcv.git
git clone https://github.com/Laughing-q/YOLO-Q.git
cd YOLO-Q
pip install -r requirements.txt
pip install -e .
```
</details>

<details open>
<summary>Export Model</summary>

* yolov5
```shell
git clone https://github.com/Laughing-q/yolov5-6.git
python export.py --weights pt_file --include=engine --device 0 --imgsz h w [--half]
```
* nanodet
```shell
git clone https://github.com/Laughing-q/nanodet.git
python tools/export_onnx.py --cfg_path cfg_file --model_path model_ckpt --out_path output_file --imgsz h w [--half]
python tools/export_trt.py --onnx-path onnx_file [--half]
```
* yolox
```shell
git clone https://github.com/Laughing-q/YOLOX-Q.git
python tools/export_onnx.py -f exp_file -c model_ckpt --imgsz h w [--half]
python tools/export_trt.py --onnx-path onnx_file [--half]
```
* yolo-fastestV2
```shell
git clone https://github.com/Laughing-q/Yolo-FastestV2.git
python pytorch2onnx.py --data data_file --weights model_ckpt --output output_file --imgsz h w [--half]
python export_trt.py --onnx-path onnx_file [--half]
```
* yolov5-lite
```shell
git clone https://github.com/Laughing-q/YOLOv5-Lite.git
# support yolov5-lite-s and yolov5-lite-g
python export.py --weights pt_file --include=engine --device 0 --imgsz h w [--half]
```

</details>

<details open>
<summary>MNN(experimental)</summary>

- numpy >=1.20.1
- yolov5
```shell
git clone https://github.com/Laughing-q/yolov5-6.git
# without `--half`
python export.py --weights pt_file --include=onnx --device 0 --imgsz h w
./MNNConvert -f ONNX --modelFile onnx_file --MNNModel mnn_file --bizCode biz [--fp16]
```

</details>

<details>
<summary>Demo</summary>

- prepare config file like below:
  * torch version
  ```vim
  model1:
    model_type: yolov5
    weight: yolov5s.pt
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null

  model2:
    model_type: yolox
    yaml: yolox_nano.yaml
    weight: yolox_nano.pth
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
  ```
  * tensorrt version(tenxorrtx)
  ```vim
  model1:
    engine_file: yolov5n.engine
    lib_file: libmyplugins.so
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
    names: name.yaml

  model2:
    engine_file: yolov5n.engine
    lib_file: libmyplugins.so
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
    names: name.yaml
  ```
  * tensorrt version(onnx -> tensorrt)
  ```vim
  model1:
    model_type: yolov5
    engine_file: yolov5n.engine
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
    names: name.yaml

  model2:
    model_type: yolox
    engine_file: yolox-nano.engine
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
    names: name.yaml

  model3:
    model_type: nanodet
    engine_file: nanodet-plus.engine
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
    names: name.yaml

  model4:
    model_type: yolo-fastestV2
    engine_file: nanodet-plus.engine
    conf_thres: 0.4
    iou_thres: 0.4
    filter: null
    names: name.yaml
  ```
- See `demo/` for more details.
</details>

## Tips
- The official weights of `yolo-fastestV2` and `nanodet-plus` trained with stretched(do not keep aspect ratio) images.
- The weights of `nanodet-plus` is compatible with stretching and kepping ratio images.
- The weights of `yolo-fastestV2` support stretching image only, or the prefermance will decline.
- I can't export `yolov5-lite-c` to engine file normally in my environment(cuda10.2, there is a issue about `cublas`), 
`trtexec --onnx=*.onnx --saveEngine=*.engine --tacticSources=-cublasLt,+cublas --workspace=2048 --fp16` command can generate an engine file, 
but can't get any detections.

## Reference
- [https://github.com/ultralytics/yolov5](https://github.com/ultralytics/yolov5)
- [https://github.com/Megvii-BaseDetection/YOLOX](https://github.com/Megvii-BaseDetection/YOLOX)
- [https://github.com/open-mmlab/mmcv](https://github.com/open-mmlab/mmcv)
