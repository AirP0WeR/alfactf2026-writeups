package io.peakmood.mobile;

import android.content.Context;
import android.graphics.SurfaceTexture;
import android.hardware.Camera;
import android.util.AttributeSet;
import android.view.TextureView;
import java.util.List;

/* JADX INFO: loaded from: classes.dex */
public class CameraPreviewView extends TextureView implements TextureView.SurfaceTextureListener {
    private Camera camera;
    private boolean previewRequested;
    private boolean surfaceReady;

    public CameraPreviewView(Context context) {
        this(context, null);
    }

    public CameraPreviewView(Context context, AttributeSet attributeSet) {
        super(context, attributeSet);
        this.previewRequested = false;
        this.surfaceReady = false;
        setSurfaceTextureListener(this);
        setOpaque(true);
    }

    public void startPreview() {
        this.previewRequested = true;
        openCameraIfPossible();
    }

    public void stopPreview() {
        this.previewRequested = false;
        releaseCamera();
    }

    @Override // android.view.TextureView.SurfaceTextureListener
    public void onSurfaceTextureAvailable(SurfaceTexture surfaceTexture, int i, int i2) {
        this.surfaceReady = true;
        openCameraIfPossible();
    }

    @Override // android.view.TextureView.SurfaceTextureListener
    public void onSurfaceTextureSizeChanged(SurfaceTexture surfaceTexture, int i, int i2) {
    }

    @Override // android.view.TextureView.SurfaceTextureListener
    public boolean onSurfaceTextureDestroyed(SurfaceTexture surfaceTexture) {
        this.surfaceReady = false;
        releaseCamera();
        return true;
    }

    @Override // android.view.TextureView.SurfaceTextureListener
    public void onSurfaceTextureUpdated(SurfaceTexture surfaceTexture) {
    }

    private void openCameraIfPossible() {
        if (!this.previewRequested || !this.surfaceReady || this.camera != null || !isAvailable()) {
            return;
        }
        try {
            int iFindBackFacingCamera = findBackFacingCamera();
            this.camera = iFindBackFacingCamera >= 0 ? Camera.open(iFindBackFacingCamera) : Camera.open();
            Camera.Parameters parameters = this.camera.getParameters();
            Camera.Size sizeChoosePreviewSize = choosePreviewSize(parameters.getSupportedPreviewSizes());
            if (sizeChoosePreviewSize != null) {
                parameters.setPreviewSize(sizeChoosePreviewSize.width, sizeChoosePreviewSize.height);
            }
            List<String> supportedFocusModes = parameters.getSupportedFocusModes();
            if (supportedFocusModes != null && supportedFocusModes.contains("continuous-picture")) {
                parameters.setFocusMode("continuous-picture");
            }
            this.camera.setParameters(parameters);
            this.camera.setDisplayOrientation(90);
            this.camera.setPreviewTexture(getSurfaceTexture());
            this.camera.startPreview();
        } catch (Exception e) {
            releaseCamera();
        }
    }

    private int findBackFacingCamera() {
        int numberOfCameras = Camera.getNumberOfCameras();
        Camera.CameraInfo cameraInfo = new Camera.CameraInfo();
        for (int i = 0; i < numberOfCameras; i++) {
            Camera.getCameraInfo(i, cameraInfo);
            if (cameraInfo.facing == 0) {
                return i;
            }
        }
        return -1;
    }

    private Camera.Size choosePreviewSize(List<Camera.Size> list) {
        if (list == null || list.isEmpty()) {
            return null;
        }
        Camera.Size size = list.get(0);
        int iAbs = Math.abs(size.width - 1280) + Math.abs(size.height - 720);
        for (Camera.Size size2 : list) {
            int iAbs2 = Math.abs(size2.width - 1280) + Math.abs(size2.height - 720);
            if (iAbs2 < iAbs) {
                size = size2;
                iAbs = iAbs2;
            }
        }
        return size;
    }

    private void releaseCamera() {
        if (this.camera == null) {
            return;
        }
        try {
            this.camera.stopPreview();
        } catch (Exception e) {
        }
        this.camera.release();
        this.camera = null;
    }
}
