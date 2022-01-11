from yolo.trt import build_trt_from_configs
from yolo.api.trt_inference import TRTPredictor
from yolo.api.visualization import Visualizer
from yolo.utils.metrics import MeterBuffer
from yolo.utils.gpu_metrics import gpu_mem_usage, gpu_use
import cv2
import argparse
import pycuda.driver as cuda
from loguru import logger
from tqdm import tqdm

global_settings = {
    "./configs/nanodet/nanodet-m_416.yaml": {
        "batch": 1,
        "model": "m_416",
        "size": (416, 416),
    },
    "./configs/nanodet/nanodet-m_640.yaml": {
        "batch": 1,
        "model": "m_416",
        "size": (384, 640),
    },
    "./configs/nanodet/nanodet-m_640-15.yaml": {
        "batch": 15,
        "model": "m_416",
        "size": (384, 640),
    },
}

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Demo of nanodet-plus(tensorrt).",
    )
    parser.add_argument(
        "--cfg-path",
        default="./configs/nanodet/nanodet-m_416.yaml",
        type=str,
        help="Path to .yml config file.",
    )
    parser.add_argument(
        "--show", action='store_true', help="Model intput shape."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    pre_multi = False  # 多线程速度较慢
    infer_multi = False  # 多线程速度较慢
    post_multi = False  # 多线程速度较慢

    device = 0
    show = args.show

    cfg_path = args.cfg_path
    warmup_frames = 100
    test_frames = 500
    setting = global_settings[cfg_path]

    test_batch = setting["batch"]
    test_model = setting["model"]
    test_size = setting["size"]

    # logger.add("trt15.log", format="{message}")
    # logger.add("trt1.log", format="{message}")
    # logger.add("trt15.log")

    model = build_trt_from_configs(cfg_path=cfg_path)
    predictor = TRTPredictor(
        img_hw=test_size,
        models=model,
        device=device,
        auto=False,
        pre_multi=pre_multi,
        infer_multi=infer_multi,
        post_multi=post_multi,
    )

    if predictor.multi_model:
        vis = [Visualizer(names=model.names) for model in predictor.models]
    else:
        vis = [Visualizer(names=predictor.models.names)]
        # vis.draw_imgs(img, outputs[i])
    # vis = Visualizer(names=model[1].names)

    meter = MeterBuffer(window_size=500)

    cap = cv2.VideoCapture("/e/1.avi")
    frames = warmup_frames + test_frames
    pbar = tqdm(range(frames), total=frames)
    for frame_num in pbar:
        ret, frame = cap.read()
        if not ret:
            break
        outputs = predictor.inference([frame for _ in range(test_batch)], post=False)
        if show:
            for i, v in enumerate(vis):
                v.draw_imgs(frame, outputs[i])
            cv2.imshow("p", frame)
            if cv2.waitKey(1) == ord("q"):
                break
        memory = gpu_mem_usage()
        utilize = gpu_use()
        pbar.desc = f"{predictor.times}, {memory}, {utilize}"
        # logger.info(f"{predictor.times}, {memory}, {utilize}")
        meter.update(memory=memory, utilize=utilize, **predictor.times)

    logger.info("-------------------------------------------------------")
    logger.info(
        f"Tensort, {test_batch}x5, nanodet-plus-{test_model}, {test_size}, {test_frames}frames average time."
    )
    logger.info(f"pre_multi: {pre_multi}")
    logger.info(f"infer_multi: {infer_multi}")
    logger.info(f"post_multi: {post_multi}")
    logger.info(f"Average preprocess: {round(meter['preprocess'].avg, 1)}ms")
    logger.info(f"Average inference: {round(meter['inference'].avg, 1)}ms")
    logger.info(f"Average postprocess: {round(meter['postprocess'].avg, 1)}ms")
    logger.info(f"Average Total: {round(meter['total'].avg, 1)}ms")
    logger.info(f"Average memory: {round(meter['memory'].avg)}MB")
    logger.info(f"Average utilize: {round(meter['utilize'].avg, 1)}%")
    logger.info(f"Max utilize: {round(meter['utilize'].max, 1)}%")
