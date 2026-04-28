.class public Lio/peakmood/mobile/CameraPreviewView;
.super Landroid/view/TextureView;
.source "CameraPreviewView.java"

# interfaces
.implements Landroid/view/TextureView$SurfaceTextureListener;


# instance fields
.field private camera:Landroid/hardware/Camera;

.field private previewRequested:Z

.field private surfaceReady:Z


# direct methods
.method public constructor <init>(Landroid/content/Context;)V
    .locals 1

    .line 18
    const/4 v0, 0x0

    invoke-direct {p0, p1, v0}, Lio/peakmood/mobile/CameraPreviewView;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;)V

    .line 19
    return-void
.end method

.method public constructor <init>(Landroid/content/Context;Landroid/util/AttributeSet;)V
    .locals 0

    .line 22
    invoke-direct {p0, p1, p2}, Landroid/view/TextureView;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;)V

    .line 14
    const/4 p1, 0x0

    iput-boolean p1, p0, Lio/peakmood/mobile/CameraPreviewView;->previewRequested:Z

    .line 15
    iput-boolean p1, p0, Lio/peakmood/mobile/CameraPreviewView;->surfaceReady:Z

    .line 23
    invoke-virtual {p0, p0}, Lio/peakmood/mobile/CameraPreviewView;->setSurfaceTextureListener(Landroid/view/TextureView$SurfaceTextureListener;)V

    .line 24
    const/4 p1, 0x1

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/CameraPreviewView;->setOpaque(Z)V

    .line 25
    return-void
.end method

.method private choosePreviewSize(Ljava/util/List;)Landroid/hardware/Camera$Size;
    .locals 5
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/List<",
            "Landroid/hardware/Camera$Size;",
            ">;)",
            "Landroid/hardware/Camera$Size;"
        }
    .end annotation

    .line 97
    if-eqz p1, :cond_3

    invoke-interface {p1}, Ljava/util/List;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_1

    .line 100
    :cond_0
    const/4 v0, 0x0

    invoke-interface {p1, v0}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/hardware/Camera$Size;

    .line 101
    iget v1, v0, Landroid/hardware/Camera$Size;->width:I

    add-int/lit16 v1, v1, -0x500

    invoke-static {v1}, Ljava/lang/Math;->abs(I)I

    move-result v1

    iget v2, v0, Landroid/hardware/Camera$Size;->height:I

    add-int/lit16 v2, v2, -0x2d0

    invoke-static {v2}, Ljava/lang/Math;->abs(I)I

    move-result v2

    add-int/2addr v1, v2

    .line 102
    invoke-interface {p1}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p1

    :goto_0
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_2

    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroid/hardware/Camera$Size;

    .line 103
    iget v3, v2, Landroid/hardware/Camera$Size;->width:I

    add-int/lit16 v3, v3, -0x500

    invoke-static {v3}, Ljava/lang/Math;->abs(I)I

    move-result v3

    iget v4, v2, Landroid/hardware/Camera$Size;->height:I

    add-int/lit16 v4, v4, -0x2d0

    invoke-static {v4}, Ljava/lang/Math;->abs(I)I

    move-result v4

    add-int/2addr v3, v4

    .line 104
    if-ge v3, v1, :cond_1

    .line 105
    nop

    .line 106
    move-object v0, v2

    move v1, v3

    .line 108
    :cond_1
    goto :goto_0

    .line 109
    :cond_2
    return-object v0

    .line 98
    :cond_3
    :goto_1
    const/4 p1, 0x0

    return-object p1
.end method

.method private findBackFacingCamera()I
    .locals 4

    .line 85
    invoke-static {}, Landroid/hardware/Camera;->getNumberOfCameras()I

    move-result v0

    .line 86
    new-instance v1, Landroid/hardware/Camera$CameraInfo;

    invoke-direct {v1}, Landroid/hardware/Camera$CameraInfo;-><init>()V

    .line 87
    const/4 v2, 0x0

    :goto_0
    if-ge v2, v0, :cond_1

    .line 88
    invoke-static {v2, v1}, Landroid/hardware/Camera;->getCameraInfo(ILandroid/hardware/Camera$CameraInfo;)V

    .line 89
    iget v3, v1, Landroid/hardware/Camera$CameraInfo;->facing:I

    if-nez v3, :cond_0

    .line 90
    return v2

    .line 87
    :cond_0
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    .line 93
    :cond_1
    const/4 v0, -0x1

    return v0
.end method

.method private openCameraIfPossible()V
    .locals 4

    .line 59
    const-string v0, "continuous-picture"

    iget-boolean v1, p0, Lio/peakmood/mobile/CameraPreviewView;->previewRequested:Z

    if-eqz v1, :cond_4

    iget-boolean v1, p0, Lio/peakmood/mobile/CameraPreviewView;->surfaceReady:Z

    if-eqz v1, :cond_4

    iget-object v1, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    if-nez v1, :cond_4

    invoke-virtual {p0}, Lio/peakmood/mobile/CameraPreviewView;->isAvailable()Z

    move-result v1

    if-nez v1, :cond_0

    goto :goto_2

    .line 64
    :cond_0
    :try_start_0
    invoke-direct {p0}, Lio/peakmood/mobile/CameraPreviewView;->findBackFacingCamera()I

    move-result v1

    .line 65
    if-ltz v1, :cond_1

    invoke-static {v1}, Landroid/hardware/Camera;->open(I)Landroid/hardware/Camera;

    move-result-object v1

    goto :goto_0

    :cond_1
    invoke-static {}, Landroid/hardware/Camera;->open()Landroid/hardware/Camera;

    move-result-object v1

    :goto_0
    iput-object v1, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    .line 66
    iget-object v1, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    invoke-virtual {v1}, Landroid/hardware/Camera;->getParameters()Landroid/hardware/Camera$Parameters;

    move-result-object v1

    .line 67
    invoke-virtual {v1}, Landroid/hardware/Camera$Parameters;->getSupportedPreviewSizes()Ljava/util/List;

    move-result-object v2

    invoke-direct {p0, v2}, Lio/peakmood/mobile/CameraPreviewView;->choosePreviewSize(Ljava/util/List;)Landroid/hardware/Camera$Size;

    move-result-object v2

    .line 68
    if-eqz v2, :cond_2

    .line 69
    iget v3, v2, Landroid/hardware/Camera$Size;->width:I

    iget v2, v2, Landroid/hardware/Camera$Size;->height:I

    invoke-virtual {v1, v3, v2}, Landroid/hardware/Camera$Parameters;->setPreviewSize(II)V

    .line 71
    :cond_2
    invoke-virtual {v1}, Landroid/hardware/Camera$Parameters;->getSupportedFocusModes()Ljava/util/List;

    move-result-object v2

    .line 72
    if-eqz v2, :cond_3

    invoke-interface {v2, v0}, Ljava/util/List;->contains(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_3

    .line 73
    invoke-virtual {v1, v0}, Landroid/hardware/Camera$Parameters;->setFocusMode(Ljava/lang/String;)V

    .line 75
    :cond_3
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    invoke-virtual {v0, v1}, Landroid/hardware/Camera;->setParameters(Landroid/hardware/Camera$Parameters;)V

    .line 76
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    const/16 v1, 0x5a

    invoke-virtual {v0, v1}, Landroid/hardware/Camera;->setDisplayOrientation(I)V

    .line 77
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    invoke-virtual {p0}, Lio/peakmood/mobile/CameraPreviewView;->getSurfaceTexture()Landroid/graphics/SurfaceTexture;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/hardware/Camera;->setPreviewTexture(Landroid/graphics/SurfaceTexture;)V

    .line 78
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    invoke-virtual {v0}, Landroid/hardware/Camera;->startPreview()V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 81
    goto :goto_1

    .line 79
    :catch_0
    move-exception v0

    .line 80
    invoke-direct {p0}, Lio/peakmood/mobile/CameraPreviewView;->releaseCamera()V

    .line 82
    :goto_1
    return-void

    .line 60
    :cond_4
    :goto_2
    return-void
.end method

.method private releaseCamera()V
    .locals 1

    .line 113
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    if-nez v0, :cond_0

    .line 114
    return-void

    .line 117
    :cond_0
    :try_start_0
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    invoke-virtual {v0}, Landroid/hardware/Camera;->stopPreview()V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 119
    goto :goto_0

    .line 118
    :catch_0
    move-exception v0

    .line 120
    :goto_0
    iget-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    invoke-virtual {v0}, Landroid/hardware/Camera;->release()V

    .line 121
    const/4 v0, 0x0

    iput-object v0, p0, Lio/peakmood/mobile/CameraPreviewView;->camera:Landroid/hardware/Camera;

    .line 122
    return-void
.end method


# virtual methods
.method public onSurfaceTextureAvailable(Landroid/graphics/SurfaceTexture;II)V
    .locals 0

    .line 39
    const/4 p1, 0x1

    iput-boolean p1, p0, Lio/peakmood/mobile/CameraPreviewView;->surfaceReady:Z

    .line 40
    invoke-direct {p0}, Lio/peakmood/mobile/CameraPreviewView;->openCameraIfPossible()V

    .line 41
    return-void
.end method

.method public onSurfaceTextureDestroyed(Landroid/graphics/SurfaceTexture;)Z
    .locals 0

    .line 49
    const/4 p1, 0x0

    iput-boolean p1, p0, Lio/peakmood/mobile/CameraPreviewView;->surfaceReady:Z

    .line 50
    invoke-direct {p0}, Lio/peakmood/mobile/CameraPreviewView;->releaseCamera()V

    .line 51
    const/4 p1, 0x1

    return p1
.end method

.method public onSurfaceTextureSizeChanged(Landroid/graphics/SurfaceTexture;II)V
    .locals 0

    .line 45
    return-void
.end method

.method public onSurfaceTextureUpdated(Landroid/graphics/SurfaceTexture;)V
    .locals 0

    .line 56
    return-void
.end method

.method public startPreview()V
    .locals 1

    .line 28
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/CameraPreviewView;->previewRequested:Z

    .line 29
    invoke-direct {p0}, Lio/peakmood/mobile/CameraPreviewView;->openCameraIfPossible()V

    .line 30
    return-void
.end method

.method public stopPreview()V
    .locals 1

    .line 33
    const/4 v0, 0x0

    iput-boolean v0, p0, Lio/peakmood/mobile/CameraPreviewView;->previewRequested:Z

    .line 34
    invoke-direct {p0}, Lio/peakmood/mobile/CameraPreviewView;->releaseCamera()V

    .line 35
    return-void
.end method
