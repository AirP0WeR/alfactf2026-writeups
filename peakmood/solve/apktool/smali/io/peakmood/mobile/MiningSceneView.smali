.class public Lio/peakmood/mobile/MiningSceneView;
.super Landroid/view/View;
.source "MiningSceneView.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;,
        Lio/peakmood/mobile/MiningSceneView$Shard;
    }
.end annotation


# static fields
.field private static final FLASH_DURATION_MS:J = 0xdcL

.field private static final SWING_DURATION_MS:J = 0x26cL


# instance fields
.field private final bitmapPaint:Landroid/graphics/Paint;

.field private final bitmapShadowPaint:Landroid/graphics/Paint;

.field private final bitmapUnderlayPaint:Landroid/graphics/Paint;

.field private final coreFillPaint:Landroid/graphics/Paint;

.field private final corePlatePaint:Landroid/graphics/Paint;

.field private final crackPaint:Landroid/graphics/Paint;

.field private damageProgress:F

.field private flashStartedAtMs:J

.field private final geodeFrames:[Landroid/graphics/Bitmap;

.field private final geodePlatePaint:Landroid/graphics/Paint;

.field private final geodeRect:Landroid/graphics/RectF;

.field private final geodeShadowRect:Landroid/graphics/RectF;

.field private final glowPaint:Landroid/graphics/Paint;

.field private hammerBitmap:Landroid/graphics/Bitmap;

.field private final hammerMatrix:Landroid/graphics/Matrix;

.field private final hammerShadowMatrix:Landroid/graphics/Matrix;

.field private nodeActive:Z

.field private nodeTapListener:Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;

.field private final ringPaint:Landroid/graphics/Paint;

.field private final shadowPaint:Landroid/graphics/Paint;

.field private final shadowRect:Landroid/graphics/RectF;

.field private final shardPaint:Landroid/graphics/Paint;

.field private final shards:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Lio/peakmood/mobile/MiningSceneView$Shard;",
            ">;"
        }
    .end annotation
.end field

.field private swingStartedAtMs:J

.field private tier:Ljava/lang/String;


# direct methods
.method public constructor <init>(Landroid/content/Context;)V
    .locals 1

    .line 59
    const/4 v0, 0x0

    invoke-direct {p0, p1, v0}, Lio/peakmood/mobile/MiningSceneView;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;)V

    .line 60
    return-void
.end method

.method public constructor <init>(Landroid/content/Context;Landroid/util/AttributeSet;)V
    .locals 7

    .line 63
    invoke-direct {p0, p1, p2}, Landroid/view/View;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;)V

    .line 31
    const/16 p1, 0xc

    new-array p2, p1, [Landroid/graphics/Bitmap;

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->geodeFrames:[Landroid/graphics/Bitmap;

    .line 32
    new-instance p2, Landroid/graphics/Paint;

    const/4 v0, 0x3

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapPaint:Landroid/graphics/Paint;

    .line 33
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    .line 34
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    .line 35
    new-instance p2, Landroid/graphics/Paint;

    const/4 v0, 0x1

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    .line 36
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->geodePlatePaint:Landroid/graphics/Paint;

    .line 37
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->coreFillPaint:Landroid/graphics/Paint;

    .line 38
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->corePlatePaint:Landroid/graphics/Paint;

    .line 39
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    .line 40
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    .line 41
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->shardPaint:Landroid/graphics/Paint;

    .line 42
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->shadowPaint:Landroid/graphics/Paint;

    .line 43
    new-instance p2, Landroid/graphics/Matrix;

    invoke-direct {p2}, Landroid/graphics/Matrix;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    .line 44
    new-instance p2, Landroid/graphics/Matrix;

    invoke-direct {p2}, Landroid/graphics/Matrix;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerShadowMatrix:Landroid/graphics/Matrix;

    .line 45
    new-instance p2, Landroid/graphics/RectF;

    invoke-direct {p2}, Landroid/graphics/RectF;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    .line 46
    new-instance p2, Landroid/graphics/RectF;

    invoke-direct {p2}, Landroid/graphics/RectF;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->shadowRect:Landroid/graphics/RectF;

    .line 47
    new-instance p2, Landroid/graphics/RectF;

    invoke-direct {p2}, Landroid/graphics/RectF;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->geodeShadowRect:Landroid/graphics/RectF;

    .line 48
    new-instance p2, Ljava/util/ArrayList;

    invoke-direct {p2}, Ljava/util/ArrayList;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->shards:Ljava/util/List;

    .line 52
    const/4 p2, 0x0

    iput-boolean p2, p0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    .line 53
    const-string p2, "none"

    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->tier:Ljava/lang/String;

    .line 54
    const/4 p2, 0x0

    iput p2, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    .line 55
    const-wide/16 v1, -0x1

    iput-wide v1, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    .line 56
    iput-wide v1, p0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    .line 64
    invoke-direct {p0}, Lio/peakmood/mobile/MiningSceneView;->loadBitmaps()V

    .line 65
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    new-instance v1, Landroid/graphics/PorterDuffColorFilter;

    const/16 v2, 0x10

    const/16 v3, 0xbe

    const/4 v4, 0x6

    invoke-static {v3, v4, p1, v2}, Landroid/graphics/Color;->argb(IIII)I

    move-result v2

    sget-object v3, Landroid/graphics/PorterDuff$Mode;->SRC_IN:Landroid/graphics/PorterDuff$Mode;

    invoke-direct {v1, v2, v3}, Landroid/graphics/PorterDuffColorFilter;-><init>(ILandroid/graphics/PorterDuff$Mode;)V

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColorFilter(Landroid/graphics/ColorFilter;)Landroid/graphics/ColorFilter;

    .line 66
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    new-instance v1, Landroid/graphics/PorterDuffColorFilter;

    const/16 v2, 0xef

    const/16 v3, 0xf2

    const/16 v5, 0xff

    const/16 v6, 0xe8

    invoke-static {v5, v6, v2, v3}, Landroid/graphics/Color;->argb(IIII)I

    move-result v2

    sget-object v3, Landroid/graphics/PorterDuff$Mode;->SRC_ATOP:Landroid/graphics/PorterDuff$Mode;

    invoke-direct {v1, v2, v3}, Landroid/graphics/PorterDuffColorFilter;-><init>(ILandroid/graphics/PorterDuff$Mode;)V

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColorFilter(Landroid/graphics/ColorFilter;)Landroid/graphics/ColorFilter;

    .line 67
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 68
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->geodePlatePaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 69
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->geodePlatePaint:Landroid/graphics/Paint;

    const/16 v1, 0xd8

    const/4 v2, 0x4

    const/16 v3, 0x8

    const/16 v6, 0xa

    invoke-static {v1, v2, v3, v6}, Landroid/graphics/Color;->argb(IIII)I

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 70
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->corePlatePaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 71
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->corePlatePaint:Landroid/graphics/Paint;

    const/16 v1, 0xfa

    invoke-static {v1, v4, v6, p1}, Landroid/graphics/Color;->argb(IIII)I

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 72
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->coreFillPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 73
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->coreFillPaint:Landroid/graphics/Paint;

    const/16 v1, 0x12

    const/16 v2, 0x16

    const/16 v3, 0xd

    invoke-static {v5, v3, v1, v2}, Landroid/graphics/Color;->argb(IIII)I

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 74
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 75
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    const v1, 0x400ccccd    # 2.2f

    invoke-direct {p0, v1}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 76
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 77
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Cap;->ROUND:Landroid/graphics/Paint$Cap;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStrokeCap(Landroid/graphics/Paint$Cap;)V

    .line 78
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Join;->ROUND:Landroid/graphics/Paint$Join;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStrokeJoin(Landroid/graphics/Paint$Join;)V

    .line 79
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->shadowPaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 80
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->shadowPaint:Landroid/graphics/Paint;

    const/4 v1, 0x7

    const/16 v2, 0x9

    const/16 v3, 0x76

    invoke-static {v3, v1, v2, p1}, Landroid/graphics/Color;->argb(IIII)I

    move-result p1

    invoke-virtual {p2, p1}, Landroid/graphics/Paint;->setColor(I)V

    .line 81
    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MiningSceneView;->setClickable(Z)V

    .line 82
    return-void
.end method

.method private boostBitmapAlpha(Landroid/graphics/Bitmap;FI)Landroid/graphics/Bitmap;
    .locals 10

    .line 93
    if-nez p1, :cond_0

    .line 94
    const/4 p1, 0x0

    return-object p1

    .line 97
    :cond_0
    sget-object v0, Landroid/graphics/Bitmap$Config;->ARGB_8888:Landroid/graphics/Bitmap$Config;

    const/4 v1, 0x1

    invoke-virtual {p1, v0, v1}, Landroid/graphics/Bitmap;->copy(Landroid/graphics/Bitmap$Config;Z)Landroid/graphics/Bitmap;

    move-result-object v2

    .line 98
    if-nez v2, :cond_1

    .line 99
    return-object p1

    .line 102
    :cond_1
    invoke-virtual {v2}, Landroid/graphics/Bitmap;->getWidth()I

    move-result v5

    .line 103
    invoke-virtual {v2}, Landroid/graphics/Bitmap;->getHeight()I

    move-result v9

    .line 104
    mul-int p1, v5, v9

    new-array v3, p1, [I

    .line 105
    const/4 v6, 0x0

    const/4 v7, 0x0

    const/4 v4, 0x0

    move v8, v5

    invoke-virtual/range {v2 .. v9}, Landroid/graphics/Bitmap;->getPixels([IIIIIII)V

    .line 106
    const/4 v0, 0x0

    :goto_0
    if-ge v0, p1, :cond_3

    .line 107
    aget v1, v3, v0

    .line 108
    invoke-static {v1}, Landroid/graphics/Color;->alpha(I)I

    move-result v4

    .line 109
    if-nez v4, :cond_2

    .line 110
    goto :goto_1

    .line 112
    :cond_2
    int-to-float v4, v4

    mul-float v4, v4, p2

    invoke-static {v4}, Ljava/lang/Math;->round(F)I

    move-result v4

    const/16 v6, 0xff

    invoke-static {v6, v4}, Ljava/lang/Math;->min(II)I

    move-result v4

    invoke-static {p3, v4}, Ljava/lang/Math;->max(II)I

    move-result v4

    .line 113
    invoke-static {v1}, Landroid/graphics/Color;->red(I)I

    move-result v6

    invoke-static {v1}, Landroid/graphics/Color;->green(I)I

    move-result v7

    invoke-static {v1}, Landroid/graphics/Color;->blue(I)I

    move-result v1

    invoke-static {v4, v6, v7, v1}, Landroid/graphics/Color;->argb(IIII)I

    move-result v1

    aput v1, v3, v0

    .line 106
    :goto_1
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 115
    :cond_3
    const/4 v6, 0x0

    const/4 v7, 0x0

    const/4 v4, 0x0

    move v8, v5

    invoke-virtual/range {v2 .. v9}, Landroid/graphics/Bitmap;->setPixels([IIIIIII)V

    .line 116
    return-object v2
.end method

.method private dp(F)F
    .locals 1

    .line 348
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float p1, p1, v0

    return p1
.end method

.method private drawCracks(Landroid/graphics/Canvas;FF)V
    .locals 12

    .line 253
    iget v0, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    const v1, 0x3d4ccccd    # 0.05f

    cmpg-float v0, v0, v1

    if-gtz v0, :cond_0

    .line 254
    return-void

    .line 256
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    const/16 v1, 0xf5

    const/16 v2, 0xff

    const/16 v3, 0xd2

    const/16 v4, 0xdc

    invoke-static {v3, v4, v1, v2}, Landroid/graphics/Color;->argb(IIII)I

    move-result v1

    invoke-virtual {v0, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 257
    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    iget v1, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    const/high16 v2, 0x40400000    # 3.0f

    mul-float v1, v1, v2

    const/high16 v2, 0x3fc00000    # 1.5f

    add-float/2addr v1, v2

    invoke-direct {p0, v1}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v1

    invoke-virtual {v0, v1}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 259
    const/high16 v0, 0x42ac0000    # 86.0f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v0

    .line 260
    iget v1, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    const/high16 v2, 0x40a00000    # 5.0f

    mul-float v1, v1, v2

    float-to-double v1, v1

    invoke-static {v1, v2}, Ljava/lang/Math;->floor(D)D

    move-result-wide v1

    double-to-int v1, v1

    const/4 v2, 0x0

    invoke-static {v2, v1}, Ljava/lang/Math;->max(II)I

    move-result v1

    add-int/lit8 v1, v1, 0x2

    .line 261
    nop

    :goto_0
    if-ge v2, v1, :cond_3

    .line 262
    int-to-double v3, v2

    const-wide v5, 0x3ff0c152382d7365L    # 1.0471975511965976

    invoke-static {v3, v4}, Ljava/lang/Double;->isNaN(D)Z

    mul-double v3, v3, v5

    const-wide v5, 0x3fd5c28f5c28f5c3L    # 0.34

    add-double/2addr v3, v5

    iget v5, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    const v6, 0x3e6147ae    # 0.22f

    mul-float v5, v5, v6

    float-to-double v5, v5

    invoke-static {v5, v6}, Ljava/lang/Double;->isNaN(D)Z

    add-double/2addr v3, v5

    double-to-float v3, v3

    .line 263
    new-instance v4, Landroid/graphics/Path;

    invoke-direct {v4}, Landroid/graphics/Path;-><init>()V

    .line 264
    float-to-double v5, v3

    invoke-static {v5, v6}, Ljava/lang/Math;->cos(D)D

    move-result-wide v7

    double-to-float v7, v7

    mul-float v7, v7, v0

    const v8, 0x3df5c28f    # 0.12f

    mul-float v7, v7, v8

    add-float/2addr v7, p2

    invoke-static {v5, v6}, Ljava/lang/Math;->sin(D)D

    move-result-wide v5

    double-to-float v5, v5

    mul-float v5, v5, v0

    mul-float v5, v5, v8

    add-float/2addr v5, p3

    invoke-virtual {v4, v7, v5}, Landroid/graphics/Path;->moveTo(FF)V

    .line 265
    const/4 v5, 0x1

    :goto_1
    const/4 v6, 0x4

    if-gt v5, v6, :cond_2

    .line 266
    rem-int/lit8 v6, v5, 0x2

    if-nez v6, :cond_1

    const v6, -0x418a3d71    # -0.24f

    goto :goto_2

    :cond_1
    const v6, 0x3e2e147b    # 0.17f

    :goto_2
    add-float/2addr v6, v3

    .line 267
    int-to-float v7, v5

    const v8, 0x3e23d70a    # 0.16f

    mul-float v7, v7, v8

    const v8, 0x3e75c28f    # 0.24f

    add-float/2addr v7, v8

    iget v8, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    const v9, 0x3da3d70a    # 0.08f

    mul-float v8, v8, v9

    add-float/2addr v7, v8

    mul-float v7, v7, v0

    .line 268
    float-to-double v8, v6

    invoke-static {v8, v9}, Ljava/lang/Math;->cos(D)D

    move-result-wide v10

    double-to-float v6, v10

    mul-float v6, v6, v7

    add-float/2addr v6, p2

    invoke-static {v8, v9}, Ljava/lang/Math;->sin(D)D

    move-result-wide v8

    double-to-float v8, v8

    mul-float v8, v8, v7

    add-float/2addr v8, p3

    invoke-virtual {v4, v6, v8}, Landroid/graphics/Path;->lineTo(FF)V

    .line 265
    add-int/lit8 v5, v5, 0x1

    goto :goto_1

    .line 270
    :cond_2
    iget-object v3, p0, Lio/peakmood/mobile/MiningSceneView;->crackPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, v4, v3}, Landroid/graphics/Canvas;->drawPath(Landroid/graphics/Path;Landroid/graphics/Paint;)V

    .line 261
    add-int/lit8 v2, v2, 0x1

    goto/16 :goto_0

    .line 272
    :cond_3
    return-void
.end method

.method private drawHammer(Landroid/graphics/Canvas;JFFFF)V
    .locals 8

    .line 275
    iget-object p4, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    if-nez p4, :cond_0

    .line 276
    return-void

    .line 278
    :cond_0
    const/high16 p4, 0x428c0000    # 70.0f

    invoke-direct {p0, p4}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result p4

    sub-float p4, p6, p4

    .line 279
    const/high16 p5, 0x43040000    # 132.0f

    invoke-direct {p0, p5}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result p5

    sub-float p5, p7, p5

    .line 280
    const/high16 v0, 0x40c00000    # 6.0f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v1

    sub-float v1, p6, v1

    .line 281
    const/high16 v2, 0x42480000    # 50.0f

    invoke-direct {p0, v2}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v2

    sub-float v2, p7, v2

    .line 282
    nop

    .line 283
    nop

    .line 285
    iget-wide v3, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    const-wide/16 v5, 0x0

    cmp-long v7, v3, v5

    if-lez v7, :cond_2

    .line 286
    iget-wide p4, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    sub-long/2addr p2, p4

    long-to-float p2, p2

    const/high16 p3, 0x441b0000    # 620.0f

    div-float/2addr p2, p3

    const/high16 p3, 0x3f800000    # 1.0f

    invoke-static {p3, p2}, Ljava/lang/Math;->min(FF)F

    move-result p2

    .line 287
    const p4, 0x3f147ae1    # 0.58f

    cmpg-float p5, p2, p4

    if-gez p5, :cond_1

    .line 288
    div-float p4, p2, p4

    goto :goto_0

    .line 289
    :cond_1
    sub-float p4, p2, p4

    const p5, 0x3ed70a3d    # 0.42f

    div-float/2addr p4, p5

    sub-float p4, p3, p4

    .line 290
    :goto_0
    const/4 p5, 0x0

    invoke-static {p3, p4}, Ljava/lang/Math;->min(FF)F

    move-result p4

    invoke-static {p5, p4}, Ljava/lang/Math;->max(FF)F

    move-result p4

    .line 291
    float-to-double p4, p4

    const-wide v3, 0x400921fb54442d18L    # Math.PI

    invoke-static {p4, p5}, Ljava/lang/Double;->isNaN(D)Z

    mul-double p4, p4, v3

    const-wide v3, 0x3fea3d70a0000000L    # 0.8199999928474426

    mul-double p4, p4, v3

    invoke-static {p4, p5}, Ljava/lang/Math;->sin(D)D

    move-result-wide p4

    double-to-float p4, p4

    .line 292
    const/high16 p5, 0x42ac0000    # 86.0f

    invoke-direct {p0, p5}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result p5

    sub-float/2addr p6, p5

    invoke-direct {p0, p6, v1, p4}, Lio/peakmood/mobile/MiningSceneView;->lerp(FFF)F

    move-result p5

    .line 293
    const/high16 p6, 0x43120000    # 146.0f

    invoke-direct {p0, p6}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result p6

    sub-float/2addr p7, p6

    invoke-direct {p0, p7, v2, p4}, Lio/peakmood/mobile/MiningSceneView;->lerp(FFF)F

    move-result p6

    .line 294
    const/high16 p7, -0x3e200000    # -28.0f

    const/high16 v1, 0x42680000    # 58.0f

    invoke-direct {p0, p7, v1, p4}, Lio/peakmood/mobile/MiningSceneView;->lerp(FFF)F

    move-result p7

    .line 295
    const v1, 0x3f6b851f    # 0.92f

    const v2, 0x3f828f5c    # 1.02f

    invoke-direct {p0, v1, v2, p4}, Lio/peakmood/mobile/MiningSceneView;->lerp(FFF)F

    move-result p4

    .line 296
    cmpl-float p2, p2, p3

    if-ltz p2, :cond_3

    .line 297
    const-wide/16 p2, -0x1

    iput-wide p2, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    goto :goto_1

    .line 285
    :cond_2
    const/high16 p7, -0x3e400000    # -24.0f

    const p2, 0x3f70a3d7    # 0.94f

    move p6, p5

    move p5, p4

    const p4, 0x3f70a3d7    # 0.94f

    .line 301
    :cond_3
    :goto_1
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {p2}, Landroid/graphics/Bitmap;->getWidth()I

    move-result p2

    int-to-float p2, p2

    mul-float p2, p2, p4

    .line 302
    iget-object p3, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {p3}, Landroid/graphics/Bitmap;->getHeight()I

    move-result p3

    int-to-float p3, p3

    mul-float p3, p3, p4

    .line 303
    iget-object v1, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    invoke-virtual {v1}, Landroid/graphics/Matrix;->reset()V

    .line 304
    iget-object v1, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    invoke-virtual {v1, p4, p4}, Landroid/graphics/Matrix;->postScale(FF)Z

    .line 305
    iget-object p4, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    neg-float p2, p2

    const v1, 0x3eb851ec    # 0.36f

    mul-float p2, p2, v1

    neg-float p3, p3

    const v1, 0x3e3851ec    # 0.18f

    mul-float p3, p3, v1

    invoke-virtual {p4, p2, p3}, Landroid/graphics/Matrix;->postTranslate(FF)Z

    .line 306
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    invoke-virtual {p2, p7}, Landroid/graphics/Matrix;->postRotate(F)Z

    .line 307
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    invoke-virtual {p2, p5, p6}, Landroid/graphics/Matrix;->postTranslate(FF)Z

    .line 308
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerShadowMatrix:Landroid/graphics/Matrix;

    iget-object p3, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    invoke-virtual {p2, p3}, Landroid/graphics/Matrix;->set(Landroid/graphics/Matrix;)V

    .line 309
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerShadowMatrix:Landroid/graphics/Matrix;

    const/high16 p3, 0x40400000    # 3.0f

    invoke-direct {p0, p3}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result p3

    invoke-direct {p0, v0}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result p4

    invoke-virtual {p2, p3, p4}, Landroid/graphics/Matrix;->postTranslate(FF)Z

    .line 310
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    const/16 p3, 0xce

    invoke-virtual {p2, p3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 311
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    iget-object p3, p0, Lio/peakmood/mobile/MiningSceneView;->hammerShadowMatrix:Landroid/graphics/Matrix;

    iget-object p4, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, p3, p4}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Matrix;Landroid/graphics/Paint;)V

    .line 312
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    const/16 p3, 0xe0

    invoke-virtual {p2, p3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 313
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    iget-object p3, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    iget-object p4, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, p3, p4}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Matrix;Landroid/graphics/Paint;)V

    .line 314
    iget-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    iget-object p3, p0, Lio/peakmood/mobile/MiningSceneView;->hammerMatrix:Landroid/graphics/Matrix;

    iget-object p4, p0, Lio/peakmood/mobile/MiningSceneView;->bitmapPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, p3, p4}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Matrix;Landroid/graphics/Paint;)V

    .line 315
    return-void
.end method

.method private drawShards(Landroid/graphics/Canvas;J)V
    .locals 9

    .line 329
    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->shards:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    .line 330
    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_1

    .line 331
    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lio/peakmood/mobile/MiningSceneView$Shard;

    .line 332
    iget-wide v2, v1, Lio/peakmood/mobile/MiningSceneView$Shard;->startedAtMs:J

    sub-long v2, p2, v2

    long-to-float v2, v2

    const/high16 v3, 0x44020000    # 520.0f

    div-float/2addr v2, v3

    .line 333
    const/high16 v3, 0x3f800000    # 1.0f

    cmpl-float v4, v2, v3

    if-ltz v4, :cond_0

    .line 334
    invoke-interface {v0}, Ljava/util/Iterator;->remove()V

    .line 335
    goto :goto_0

    .line 337
    :cond_0
    sub-float/2addr v3, v2

    .line 338
    iget v4, v1, Lio/peakmood/mobile/MiningSceneView$Shard;->speed:F

    mul-float v4, v4, v2

    const/high16 v5, 0x42400000    # 48.0f

    invoke-direct {p0, v5}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v5

    mul-float v4, v4, v5

    .line 339
    iget-object v5, p0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    invoke-virtual {v5}, Landroid/graphics/RectF;->centerX()F

    move-result v5

    iget v6, v1, Lio/peakmood/mobile/MiningSceneView$Shard;->angle:F

    float-to-double v6, v6

    invoke-static {v6, v7}, Ljava/lang/Math;->cos(D)D

    move-result-wide v6

    double-to-float v6, v6

    mul-float v6, v6, v4

    add-float/2addr v5, v6

    .line 340
    iget-object v6, p0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    invoke-virtual {v6}, Landroid/graphics/RectF;->centerY()F

    move-result v6

    iget v7, v1, Lio/peakmood/mobile/MiningSceneView$Shard;->angle:F

    float-to-double v7, v7

    invoke-static {v7, v8}, Ljava/lang/Math;->sin(D)D

    move-result-wide v7

    double-to-float v7, v7

    mul-float v7, v7, v4

    add-float/2addr v6, v7

    const/high16 v4, 0x41b00000    # 22.0f

    invoke-direct {p0, v4}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v4

    mul-float v2, v2, v4

    sub-float/2addr v6, v2

    .line 341
    iget-object v2, p0, Lio/peakmood/mobile/MiningSceneView;->shardPaint:Landroid/graphics/Paint;

    iget v1, v1, Lio/peakmood/mobile/MiningSceneView$Shard;->color:I

    invoke-virtual {v2, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 342
    iget-object v1, p0, Lio/peakmood/mobile/MiningSceneView;->shardPaint:Landroid/graphics/Paint;

    const/high16 v2, 0x43340000    # 180.0f

    mul-float v2, v2, v3

    float-to-int v2, v2

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 343
    const v1, 0x4019999a    # 2.4f

    mul-float v3, v3, v1

    const/high16 v1, 0x40000000    # 2.0f

    add-float/2addr v3, v1

    invoke-direct {p0, v3}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v1

    iget-object v2, p0, Lio/peakmood/mobile/MiningSceneView;->shardPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, v5, v6, v1, v2}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 344
    goto :goto_0

    .line 345
    :cond_1
    return-void
.end method

.method private lerp(FFF)F
    .locals 0

    .line 352
    sub-float/2addr p2, p1

    mul-float p2, p2, p3

    add-float/2addr p1, p2

    return p1
.end method

.method private loadBitmaps()V
    .locals 5

    .line 85
    const/4 v0, 0x0

    :goto_0
    iget-object v1, p0, Lio/peakmood/mobile/MiningSceneView;->geodeFrames:[Landroid/graphics/Bitmap;

    array-length v1, v1

    if-ge v0, v1, :cond_1

    .line 86
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "ar_geode_"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const/16 v3, 0xa

    if-ge v0, v3, :cond_0

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "0"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    goto :goto_1

    :cond_0
    invoke-static {v0}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;

    move-result-object v3

    :goto_1
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->getContext()Landroid/content/Context;

    move-result-object v3

    invoke-virtual {v3}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v3

    const-string v4, "drawable"

    invoke-virtual {v1, v2, v4, v3}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result v1

    .line 87
    iget-object v2, p0, Lio/peakmood/mobile/MiningSceneView;->geodeFrames:[Landroid/graphics/Bitmap;

    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->getResources()Landroid/content/res/Resources;

    move-result-object v3

    invoke-static {v3, v1}, Landroid/graphics/BitmapFactory;->decodeResource(Landroid/content/res/Resources;I)Landroid/graphics/Bitmap;

    move-result-object v1

    const v3, 0x4019999a    # 2.4f

    const/16 v4, 0x6c

    invoke-direct {p0, v1, v3, v4}, Lio/peakmood/mobile/MiningSceneView;->boostBitmapAlpha(Landroid/graphics/Bitmap;FI)Landroid/graphics/Bitmap;

    move-result-object v1

    aput-object v1, v2, v0

    .line 85
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 89
    :cond_1
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    const v1, 0x7f020011

    invoke-static {v0, v1}, Landroid/graphics/BitmapFactory;->decodeResource(Landroid/content/res/Resources;I)Landroid/graphics/Bitmap;

    move-result-object v0

    const v1, 0x40466666    # 3.1f

    const/16 v2, 0x7e

    invoke-direct {p0, v0, v1, v2}, Lio/peakmood/mobile/MiningSceneView;->boostBitmapAlpha(Landroid/graphics/Bitmap;FI)Landroid/graphics/Bitmap;

    move-result-object v0

    iput-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->hammerBitmap:Landroid/graphics/Bitmap;

    .line 90
    return-void
.end method

.method private spawnShards(J)V
    .locals 8

    .line 318
    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->shards:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    .line 319
    nop

    .line 320
    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->tier:Ljava/lang/String;

    invoke-direct {p0, v0}, Lio/peakmood/mobile/MiningSceneView;->tierColor(Ljava/lang/String;)I

    move-result v6

    .line 321
    const/4 v0, 0x0

    :goto_0
    const/16 v1, 0x9

    if-ge v0, v1, :cond_0

    .line 322
    const-wide v2, 0x401921fb54442d18L    # 6.283185307179586

    int-to-double v4, v0

    invoke-static {v4, v5}, Ljava/lang/Double;->isNaN(D)Z

    mul-double v4, v4, v2

    int-to-double v1, v1

    invoke-static {v1, v2}, Ljava/lang/Double;->isNaN(D)Z

    div-double/2addr v4, v1

    const-wide v1, 0x3fc70a3d70a3d70aL    # 0.18

    add-double/2addr v4, v1

    double-to-float v2, v4

    .line 323
    int-to-float v1, v0

    const v3, 0x3e851eb8    # 0.26f

    mul-float v1, v1, v3

    const v3, 0x3fe66666    # 1.8f

    add-float/2addr v1, v3

    invoke-direct {p0, v1}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v3

    .line 324
    iget-object v7, p0, Lio/peakmood/mobile/MiningSceneView;->shards:Ljava/util/List;

    new-instance v1, Lio/peakmood/mobile/MiningSceneView$Shard;

    move-wide v4, p1

    invoke-direct/range {v1 .. v6}, Lio/peakmood/mobile/MiningSceneView$Shard;-><init>(FFJI)V

    invoke-interface {v7, v1}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 321
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 326
    :cond_0
    return-void
.end method

.method private tierColor(Ljava/lang/String;)I
    .locals 1

    .line 356
    const-string v0, "common"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 357
    const-string p1, "#6BD8C6"

    invoke-static {p1}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result p1

    return p1

    .line 359
    :cond_0
    const-string v0, "rare"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 360
    const-string p1, "#7DB0FF"

    invoke-static {p1}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result p1

    return p1

    .line 362
    :cond_1
    const-string v0, "epic"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    .line 363
    const-string p1, "#FFB766"

    invoke-static {p1}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result p1

    return p1

    .line 365
    :cond_2
    const-string v0, "FLAG"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    .line 366
    const-string p1, "#FF7363"

    invoke-static {p1}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result p1

    return p1

    .line 368
    :cond_3
    const-string p1, "#9EF2DE"

    invoke-static {p1}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result p1

    return p1
.end method


# virtual methods
.method public clearNode()V
    .locals 2

    .line 124
    const/4 v0, 0x0

    iput-boolean v0, p0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    .line 125
    const-string v0, "none"

    iput-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->tier:Ljava/lang/String;

    .line 126
    const/4 v0, 0x0

    iput v0, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    .line 127
    const-wide/16 v0, -0x1

    iput-wide v0, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    .line 128
    iput-wide v0, p0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    .line 129
    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->shards:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    .line 130
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->invalidate()V

    .line 131
    return-void
.end method

.method public isImpactAnimationRunning()Z
    .locals 6

    .line 147
    iget-wide v0, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    const-wide/16 v2, 0x0

    const/4 v4, 0x0

    cmp-long v5, v0, v2

    if-gtz v5, :cond_0

    .line 148
    return v4

    .line 150
    :cond_0
    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J

    move-result-wide v0

    iget-wide v2, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    sub-long/2addr v0, v2

    const-wide/16 v2, 0x26c

    cmp-long v5, v0, v2

    if-gez v5, :cond_1

    const/4 v4, 0x1

    :cond_1
    return v4
.end method

.method protected onDraw(Landroid/graphics/Canvas;)V
    .locals 22

    .line 182
    move-object/from16 v0, p0

    move-object/from16 v1, p1

    invoke-super/range {p0 .. p1}, Landroid/view/View;->onDraw(Landroid/graphics/Canvas;)V

    .line 183
    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J

    move-result-wide v2

    .line 184
    invoke-virtual {v0}, Lio/peakmood/mobile/MiningSceneView;->getWidth()I

    move-result v4

    int-to-float v4, v4

    .line 185
    invoke-virtual {v0}, Lio/peakmood/mobile/MiningSceneView;->getHeight()I

    move-result v5

    int-to-float v5, v5

    .line 186
    const/high16 v6, 0x3f000000    # 0.5f

    const/high16 v7, 0x3f000000    # 0.5f

    mul-float v6, v4, v7

    .line 187
    const v8, 0x3f23d70a    # 0.64f

    mul-float v8, v8, v5

    .line 188
    iget-boolean v9, v0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    if-eqz v9, :cond_0

    long-to-float v9, v2

    const v11, 0x3b102de0    # 0.0022f

    mul-float v9, v9, v11

    float-to-double v11, v9

    invoke-static {v11, v12}, Ljava/lang/Math;->sin(D)D

    move-result-wide v11

    double-to-float v9, v11

    const/high16 v11, 0x40e00000    # 7.0f

    invoke-direct {v0, v11}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v11

    mul-float v9, v9, v11

    goto :goto_0

    :cond_0
    const/4 v9, 0x0

    .line 189
    :goto_0
    iget-boolean v11, v0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    const/high16 v12, 0x3f800000    # 1.0f

    if-eqz v11, :cond_1

    long-to-float v11, v2

    const v13, 0x3b4b295f    # 0.0031f

    mul-float v11, v11, v13

    float-to-double v13, v11

    invoke-static {v13, v14}, Ljava/lang/Math;->sin(D)D

    move-result-wide v13

    double-to-float v11, v13

    const v13, 0x3ca3d70a    # 0.02f

    mul-float v11, v11, v13

    add-float/2addr v11, v12

    goto :goto_1

    :cond_1
    const/high16 v11, 0x3f800000    # 1.0f

    .line 191
    :goto_1
    iget-boolean v13, v0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    if-eqz v13, :cond_4

    .line 192
    iget-object v13, v0, Lio/peakmood/mobile/MiningSceneView;->tier:Ljava/lang/String;

    invoke-direct {v0, v13}, Lio/peakmood/mobile/MiningSceneView;->tierColor(Ljava/lang/String;)I

    move-result v13

    .line 193
    const/high16 v16, 0x3f000000    # 0.5f

    iget-object v7, v0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    invoke-virtual {v7, v13}, Landroid/graphics/Paint;->setColor(I)V

    .line 194
    iget-object v7, v0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    const/16 v17, 0x0

    long-to-float v10, v2

    const v18, 0x3b79096c    # 0.0038f

    mul-float v10, v10, v18

    const-wide/16 v18, 0x0

    float-to-double v14, v10

    invoke-static {v14, v15}, Ljava/lang/Math;->sin(D)D

    move-result-wide v14

    const-wide/high16 v20, 0x3fe0000000000000L    # 0.5

    mul-double v14, v14, v20

    add-double v14, v14, v20

    const-wide/high16 v20, 0x4032000000000000L    # 18.0

    mul-double v14, v14, v20

    double-to-int v10, v14

    add-int/lit8 v10, v10, 0x24

    invoke-virtual {v7, v10}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 195
    add-float v7, v8, v9

    iget v10, v0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    const/high16 v14, 0x41a00000    # 20.0f

    mul-float v10, v10, v14

    const/high16 v14, 0x430e0000    # 142.0f

    add-float/2addr v10, v14

    invoke-direct {v0, v10}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v14, v0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v14}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 197
    const/high16 v10, 0x42f40000    # 122.0f

    invoke-direct {v0, v10}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v14, v0, Lio/peakmood/mobile/MiningSceneView;->geodePlatePaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v14}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 198
    const/high16 v10, 0x42d40000    # 106.0f

    invoke-direct {v0, v10}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v14, v0, Lio/peakmood/mobile/MiningSceneView;->corePlatePaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v14}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 199
    const/high16 v10, 0x42c00000    # 96.0f

    invoke-direct {v0, v10}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v14, v0, Lio/peakmood/mobile/MiningSceneView;->coreFillPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v14}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 201
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v10, v13}, Landroid/graphics/Paint;->setColor(I)V

    .line 202
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    const/16 v13, 0x9e

    invoke-virtual {v10, v13}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 203
    const/high16 v10, 0x42e80000    # 116.0f

    invoke-direct {v0, v10}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v13, v0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v13}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 204
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    const/16 v13, 0x76

    invoke-virtual {v10, v13}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 205
    const/high16 v10, 0x43060000    # 134.0f

    invoke-direct {v0, v10}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v13, v0, Lio/peakmood/mobile/MiningSceneView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v13}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 207
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->shadowRect:Landroid/graphics/RectF;

    const/high16 v13, 0x42ec0000    # 118.0f

    invoke-direct {v0, v13}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v14

    sub-float v14, v6, v14

    const/high16 v15, 0x42d80000    # 108.0f

    invoke-direct {v0, v15}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v15

    add-float/2addr v15, v8

    invoke-direct {v0, v13}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v13

    add-float/2addr v13, v6

    const/high16 v12, 0x43180000    # 152.0f

    invoke-direct {v0, v12}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v12

    add-float/2addr v12, v8

    invoke-virtual {v10, v14, v15, v13, v12}, Landroid/graphics/RectF;->set(FFFF)V

    .line 208
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->shadowRect:Landroid/graphics/RectF;

    iget-object v12, v0, Lio/peakmood/mobile/MiningSceneView;->shadowPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v12}, Landroid/graphics/Canvas;->drawOval(Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 210
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->geodeFrames:[Landroid/graphics/Bitmap;

    const-wide/16 v12, 0x5a

    div-long v12, v2, v12

    iget-object v14, v0, Lio/peakmood/mobile/MiningSceneView;->geodeFrames:[Landroid/graphics/Bitmap;

    array-length v14, v14

    int-to-long v14, v14

    rem-long/2addr v12, v14

    long-to-int v13, v12

    aget-object v10, v10, v13

    .line 211
    const/high16 v12, 0x43760000    # 246.0f

    invoke-direct {v0, v12}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v12

    mul-float v12, v12, v11

    .line 212
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    mul-float v12, v12, v16

    sub-float v13, v6, v12

    sub-float v14, v8, v12

    add-float/2addr v14, v9

    add-float v15, v6, v12

    add-float/2addr v12, v8

    add-float/2addr v12, v9

    invoke-virtual {v11, v13, v14, v15, v12}, Landroid/graphics/RectF;->set(FFFF)V

    .line 213
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeShadowRect:Landroid/graphics/RectF;

    iget-object v12, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    invoke-virtual {v11, v12}, Landroid/graphics/RectF;->set(Landroid/graphics/RectF;)V

    .line 214
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeShadowRect:Landroid/graphics/RectF;

    const/high16 v12, 0x40400000    # 3.0f

    invoke-direct {v0, v12}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v12

    const/high16 v13, 0x41000000    # 8.0f

    invoke-direct {v0, v13}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v13

    invoke-virtual {v11, v12, v13}, Landroid/graphics/RectF;->offset(FF)V

    .line 216
    iget-wide v11, v0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    const/16 v14, 0xd6

    const/4 v15, 0x0

    cmp-long v16, v11, v18

    if-lez v16, :cond_3

    .line 217
    iget-wide v11, v0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    sub-long v11, v2, v11

    long-to-float v11, v11

    const/high16 v12, 0x435c0000    # 220.0f

    div-float/2addr v11, v12

    const/high16 v12, 0x3f800000    # 1.0f

    invoke-static {v12, v11}, Ljava/lang/Math;->min(FF)F

    move-result v11

    sub-float/2addr v12, v11

    .line 218
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    invoke-virtual {v11, v14}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 219
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeShadowRect:Landroid/graphics/RectF;

    iget-object v13, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v15, v11, v13}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 220
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    invoke-virtual {v11, v14}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 221
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    iget-object v13, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v15, v11, v13}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 222
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapPaint:Landroid/graphics/Paint;

    const/16 v13, 0xff

    invoke-virtual {v11, v13}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 223
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    iget-object v13, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v15, v11, v13}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 224
    cmpl-float v10, v12, v17

    if-lez v10, :cond_2

    .line 225
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    const/4 v11, -0x1

    invoke-virtual {v10, v11}, Landroid/graphics/Paint;->setColor(I)V

    .line 226
    iget-object v10, v0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    const/high16 v11, 0x42d00000    # 104.0f

    mul-float v13, v12, v11

    float-to-int v13, v13

    invoke-virtual {v10, v13}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 227
    const/high16 v10, 0x42080000    # 34.0f

    mul-float v12, v12, v10

    add-float/2addr v12, v11

    invoke-direct {v0, v12}, Lio/peakmood/mobile/MiningSceneView;->dp(F)F

    move-result v10

    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->glowPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6, v7, v10, v11}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    goto :goto_2

    .line 229
    :cond_2
    const-wide/16 v10, -0x1

    iput-wide v10, v0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    .line 231
    :goto_2
    goto :goto_3

    .line 232
    :cond_3
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    invoke-virtual {v11, v14}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 233
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeShadowRect:Landroid/graphics/RectF;

    iget-object v12, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapShadowPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v15, v11, v12}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 234
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    invoke-virtual {v11, v14}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 235
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    iget-object v12, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapUnderlayPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v15, v11, v12}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 236
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapPaint:Landroid/graphics/Paint;

    const/16 v13, 0xff

    invoke-virtual {v11, v13}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 237
    iget-object v11, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    iget-object v12, v0, Lio/peakmood/mobile/MiningSceneView;->bitmapPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v10, v15, v11, v12}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 240
    :goto_3
    invoke-direct {v0, v1, v6, v7}, Lio/peakmood/mobile/MiningSceneView;->drawCracks(Landroid/graphics/Canvas;FF)V

    .line 241
    invoke-direct {v0, v1, v2, v3}, Lio/peakmood/mobile/MiningSceneView;->drawShards(Landroid/graphics/Canvas;J)V

    .line 242
    goto :goto_4

    .line 243
    :cond_4
    const-wide/16 v18, 0x0

    iget-object v7, v0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    invoke-virtual {v7}, Landroid/graphics/RectF;->setEmpty()V

    .line 246
    :goto_4
    add-float v7, v8, v9

    invoke-direct/range {v0 .. v7}, Lio/peakmood/mobile/MiningSceneView;->drawHammer(Landroid/graphics/Canvas;JFFFF)V

    .line 247
    iget-boolean v1, v0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    if-nez v1, :cond_5

    iget-wide v1, v0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    cmp-long v3, v1, v18

    if-gtz v3, :cond_5

    iget-object v1, v0, Lio/peakmood/mobile/MiningSceneView;->shards:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_6

    .line 248
    :cond_5
    invoke-virtual {v0}, Lio/peakmood/mobile/MiningSceneView;->postInvalidateOnAnimation()V

    .line 250
    :cond_6
    return-void
.end method

.method public onTouchEvent(Landroid/view/MotionEvent;)Z
    .locals 3

    .line 167
    iget-boolean v0, p0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    if-eqz v0, :cond_3

    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->nodeTapListener:Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;

    if-nez v0, :cond_0

    goto :goto_0

    .line 170
    :cond_0
    invoke-virtual {p1}, Landroid/view/MotionEvent;->getAction()I

    move-result v0

    const/4 v1, 0x1

    if-ne v0, v1, :cond_2

    iget-object v0, p0, Lio/peakmood/mobile/MiningSceneView;->geodeRect:Landroid/graphics/RectF;

    invoke-virtual {p1}, Landroid/view/MotionEvent;->getX()F

    move-result v2

    invoke-virtual {p1}, Landroid/view/MotionEvent;->getY()F

    move-result p1

    invoke-virtual {v0, v2, p1}, Landroid/graphics/RectF;->contains(FF)Z

    move-result p1

    if-eqz p1, :cond_2

    .line 171
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->isImpactAnimationRunning()Z

    move-result p1

    if-eqz p1, :cond_1

    .line 172
    return v1

    .line 174
    :cond_1
    iget-object p1, p0, Lio/peakmood/mobile/MiningSceneView;->nodeTapListener:Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;

    invoke-interface {p1}, Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;->onNodeTap()V

    .line 175
    return v1

    .line 177
    :cond_2
    return v1

    .line 168
    :cond_3
    :goto_0
    invoke-super {p0, p1}, Landroid/view/View;->onTouchEvent(Landroid/view/MotionEvent;)Z

    move-result p1

    return p1
.end method

.method public setNodeState(ZLjava/lang/String;II)V
    .locals 0

    .line 134
    iput-boolean p1, p0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    .line 135
    if-nez p2, :cond_0

    const-string p2, "none"

    :cond_0
    iput-object p2, p0, Lio/peakmood/mobile/MiningSceneView;->tier:Ljava/lang/String;

    .line 136
    if-eqz p1, :cond_2

    if-gtz p4, :cond_1

    goto :goto_0

    .line 141
    :cond_1
    int-to-float p1, p3

    int-to-float p2, p4

    div-float/2addr p1, p2

    const/high16 p2, 0x3f800000    # 1.0f

    sub-float/2addr p2, p1

    iput p2, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    goto :goto_1

    .line 137
    :cond_2
    :goto_0
    const/4 p1, 0x0

    iput p1, p0, Lio/peakmood/mobile/MiningSceneView;->damageProgress:F

    .line 138
    const-wide/16 p1, -0x1

    iput-wide p1, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    .line 139
    iput-wide p1, p0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    .line 143
    :goto_1
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->invalidate()V

    .line 144
    return-void
.end method

.method public setOnNodeTapListener(Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;)V
    .locals 0

    .line 120
    iput-object p1, p0, Lio/peakmood/mobile/MiningSceneView;->nodeTapListener:Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;

    .line 121
    return-void
.end method

.method public triggerImpact()Z
    .locals 2

    .line 154
    iget-boolean v0, p0, Lio/peakmood/mobile/MiningSceneView;->nodeActive:Z

    if-eqz v0, :cond_1

    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->isImpactAnimationRunning()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    .line 157
    :cond_0
    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J

    move-result-wide v0

    .line 158
    iput-wide v0, p0, Lio/peakmood/mobile/MiningSceneView;->swingStartedAtMs:J

    .line 159
    iput-wide v0, p0, Lio/peakmood/mobile/MiningSceneView;->flashStartedAtMs:J

    .line 160
    invoke-direct {p0, v0, v1}, Lio/peakmood/mobile/MiningSceneView;->spawnShards(J)V

    .line 161
    invoke-virtual {p0}, Lio/peakmood/mobile/MiningSceneView;->invalidate()V

    .line 162
    const/4 v0, 0x1

    return v0

    .line 155
    :cond_1
    :goto_0
    const/4 v0, 0x0

    return v0
.end method
