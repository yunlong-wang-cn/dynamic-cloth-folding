import pyrealsense2 as rs
import argparse
import cv2
import numpy as np
import torch
# Create a context object. This object owns the handles to all connected realsense devices


def main(folder):
    pipeline = rs.pipeline()

    config = rs.config()
    config.enable_stream(rs.stream.infrared, 1, 848, 100, rs.format.y8, 300)
    selection = pipeline.start(config)

    selected_device = selection.get_device()
    depth_sensor = selected_device.first_depth_sensor()
    print(depth_sensor)
    depth_sensor.set_option(rs.option.laser_power, 0.0)

    model = torch.jit.load(f'{folder}/60_policy.pt')
    saved_image = 0
    while True:
        frames = pipeline.wait_for_frames()
        inf = frames.get_infrared_frame()

        inf_data = inf.as_frame().get_data()

        image = np.asanyarray(inf_data).astype("float32")/255
        

        

        width_start = int(848/2 - 100/2)

        image = image[:, width_start:width_start+100]


        image_tens = torch.from_numpy(image.flatten()).view(1,-1)


        _, _, corners, _ = model(image_tens)

        corners = corners.detach().numpy().flatten()



        print(corners)

        dotted_image = image.copy()

        for aux_idx in range(int(corners.shape[0]/2)):
            print(aux_idx)
            aux_u = int(corners[aux_idx*2]*100)
            aux_v = int(corners[aux_idx*2+1]*100)
            cv2.circle(dotted_image, (aux_u, aux_v), 2, (0, 255, 0), -1)



        cv2.imshow("test", dotted_image)

        cv2.imwrite(f"{folder}/living_room_test_images/wipe/{saved_image}.png", image*255)
        saved_image += 1
        print("got frames")
        cv2.waitKey(300)









if __name__ == "__main__":
    parser = argparse.ArgumentParser("Parser")
    parser.add_argument('folder', type=str)

    args = parser.parse_args()
    main(args.folder)