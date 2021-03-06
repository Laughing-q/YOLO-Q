from .detectors.yolov5 import Model
from .detectors.yolox import YOLOX
from .layers.yolo_head import YOLOXHead
from .layers.yolo_pafpn import YOLOPAFPN
from ..utils.torch_utils import select_device
import torch
import torch.nn as nn
from omegaconf import OmegaConf
from yolov5.models import attempt_load

yolox_type = {
    "nano": {"depth": 0.33, "width": 0.25, "depthwise": True,},
    "tiny": {"depth": 0.33, "width": 0.375, "depthwise": False,},
    "s": {"depth": 0.33, "width": 0.50, "depthwise": False,},
    "m": {"depth": 0.67, "width": 0.75, "depthwise": False,},
    "l": {"depth": 1.0, "width": 1.0, "depthwise": False,},
    "x": {"depth": 1.33, "width": 1.25, "depthwise": False,},
}

def build_yolov5(weight_path, device, half=True):
    device = select_device(device)
    # TODO, device may move to `Predictor`
    with torch.no_grad():
        model = attempt_load(weight_path, map_location=device)
        model.device = device
        if half:
            model.half()
    return model

def build_yolox(cfg, weight_path, device, half=True):
    def init_yolo(M):
        for m in M.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eps = 1e-3
                m.momentum = 0.03

    with open(cfg, 'r') as f:
        cfg = OmegaConf.load(f)
    model_cfg = yolox_type[cfg.type]
    in_channels = [256, 512, 1024]
    backbone = YOLOPAFPN(model_cfg['depth'], model_cfg['width'], in_channels=in_channels, depthwise=model_cfg['depthwise'])
    head = YOLOXHead(cfg.nc, model_cfg['width'], in_channels=in_channels, depthwise=model_cfg['depthwise'])
    model = YOLOX(backbone, head)
    setattr(model, 'names', cfg.names)

    model.apply(init_yolo)
    model.head.initialize_biases(1e-2)

    # load checkpoint
    # TODO, torch.no_grad() support inference only.
    # TODO, device may move to `Predictor`
    device = select_device(device)
    with torch.no_grad():
        model.to(device).eval()
        ckpt = torch.load(weight_path, map_location="cpu")
        model.load_state_dict(ckpt["model"])
        if half:
            model.half()
    return model

def build_from_configs(config):
    if isinstance(config, str):
        with open(config, "r") as f:
            config = OmegaConf.load(f)

    model_list = []
    device = config.get('device', '0')
    for _, v in config.items():
        assert v.model_type in ['yolov5', 'yolox']
        if v.model_type == 'yolov5':
            builder = build_yolov5
        else:
            builder = build_yolox
        model = builder(weight_path=v.weight,
                        device=device)
        setattr(model, 'model_type', v.model_type)
        setattr(model, 'conf_thres', v.conf_thres)
        setattr(model, 'iou_thres', v.iou_thres)
        setattr(model, 'filter', v.filter)
        model_list.append(model)
    if len(config) > 1:
        return model_list
    else:
        return model_list[0]
