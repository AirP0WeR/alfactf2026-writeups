.class public final Lio/peakmood/mobile/TerrainModel;
.super Ljava/lang/Object;
.source "TerrainModel.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lio/peakmood/mobile/TerrainModel$AnchorMatch;,
        Lio/peakmood/mobile/TerrainModel$ReliefAnchor;,
        Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;,
        Lio/peakmood/mobile/TerrainModel$BucketCoordinate;
    }
.end annotation


# static fields
.field private static final BUCKET_STEP_DEGREES:D = 6.0

.field private static final GLOBAL_RELIEF_HEIGHT:I = 0x5a0

.field private static final GLOBAL_RELIEF_STEP_MILLI_M:I = 0x13ca7

.field private static final GLOBAL_RELIEF_WIDTH:I = 0xb40

.field private static final GLOBAL_RELIEF_ZERO:I = 0x80

.field private static final LAT_BUCKET_COUNT:I = 0x1e

.field private static final LON_BUCKET_COUNT:I = 0x3c

.field private static volatile instance:Lio/peakmood/mobile/TerrainModel;


# instance fields
.field private final anchorIndex:Ljava/util/Map;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Map<",
            "Ljava/lang/Long;",
            "Ljava/util/List<",
            "Lio/peakmood/mobile/TerrainModel$ReliefAnchor;",
            ">;>;"
        }
    .end annotation
.end field

.field private final anchors:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Lio/peakmood/mobile/TerrainModel$ReliefAnchor;",
            ">;"
        }
    .end annotation
.end field

.field private final globalReliefBitmap:Landroid/graphics/Bitmap;


# direct methods
.method private constructor <init>(Landroid/content/Context;)V
    .locals 2

    .line 47
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 48
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    .line 49
    invoke-virtual {p1}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    invoke-direct {p0, v1, v0}, Lio/peakmood/mobile/TerrainModel;->loadSpecialAnchors(Landroid/content/res/Resources;Ljava/util/List;)V

    .line 50
    invoke-static {v0}, Ljava/util/Collections;->unmodifiableList(Ljava/util/List;)Ljava/util/List;

    move-result-object v1

    iput-object v1, p0, Lio/peakmood/mobile/TerrainModel;->anchors:Ljava/util/List;

    .line 51
    invoke-direct {p0, v0}, Lio/peakmood/mobile/TerrainModel;->buildAnchorIndex(Ljava/util/List;)Ljava/util/Map;

    move-result-object v0

    iput-object v0, p0, Lio/peakmood/mobile/TerrainModel;->anchorIndex:Ljava/util/Map;

    .line 52
    invoke-virtual {p1}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object p1

    invoke-direct {p0, p1}, Lio/peakmood/mobile/TerrainModel;->loadGlobalReliefBitmap(Landroid/content/res/Resources;)Landroid/graphics/Bitmap;

    move-result-object p1

    iput-object p1, p0, Lio/peakmood/mobile/TerrainModel;->globalReliefBitmap:Landroid/graphics/Bitmap;

    .line 53
    return-void
.end method

.method private static bucketCoordinate(DD)Lio/peakmood/mobile/TerrainModel$BucketCoordinate;
    .locals 4

    .line 172
    const-wide v0, 0x40567ffffbce4218L    # 89.999999

    invoke-static {v0, v1, p0, p1}, Ljava/lang/Math;->min(DD)D

    move-result-wide p0

    const-wide v0, -0x3fa980000431bde8L    # -89.999999

    invoke-static {v0, v1, p0, p1}, Ljava/lang/Math;->max(DD)D

    move-result-wide p0

    .line 173
    invoke-static {p2, p3}, Lio/peakmood/mobile/TerrainModel;->normalizeLon(D)D

    move-result-wide p2

    .line 174
    const-wide v0, 0x4056800000000000L    # 90.0

    add-double/2addr p0, v0

    const-wide/high16 v0, 0x4018000000000000L    # 6.0

    div-double/2addr p0, v0

    invoke-static {p0, p1}, Ljava/lang/Math;->floor(D)D

    move-result-wide p0

    double-to-int p0, p0

    .line 175
    const-wide v2, 0x4066800000000000L    # 180.0

    add-double/2addr p2, v2

    div-double/2addr p2, v0

    invoke-static {p2, p3}, Ljava/lang/Math;->floor(D)D

    move-result-wide p1

    double-to-int p1, p1

    rem-int/lit8 p1, p1, 0x3c

    .line 176
    const/16 p2, 0x1d

    invoke-static {p2, p0}, Ljava/lang/Math;->min(II)I

    move-result p0

    const/4 p2, 0x0

    invoke-static {p2, p0}, Ljava/lang/Math;->max(II)I

    move-result p0

    .line 177
    add-int/lit8 p1, p1, 0x3c

    rem-int/lit8 p1, p1, 0x3c

    .line 178
    new-instance p2, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;

    invoke-direct {p2, p0, p1}, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;-><init>(II)V

    return-object p2
.end method

.method private static bucketKey(II)J
    .locals 4

    .line 190
    int-to-long v0, p0

    const/16 p0, 0x20

    shl-long/2addr v0, p0

    int-to-long p0, p1

    const-wide v2, 0xffffffffL

    and-long/2addr p0, v2

    xor-long/2addr p0, v0

    return-wide p0
.end method

.method private buildAnchorIndex(Ljava/util/List;)Ljava/util/Map;
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/List<",
            "Lio/peakmood/mobile/TerrainModel$ReliefAnchor;",
            ">;)",
            "Ljava/util/Map<",
            "Ljava/lang/Long;",
            "Ljava/util/List<",
            "Lio/peakmood/mobile/TerrainModel$ReliefAnchor;",
            ">;>;"
        }
    .end annotation

    .line 157
    new-instance v0, Ljava/util/HashMap;

    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V

    .line 158
    invoke-interface {p1}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p1

    :goto_0
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_1

    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    .line 159
    iget-wide v2, v1, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lat:D

    iget-wide v4, v1, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lon:D

    invoke-static {v2, v3, v4, v5}, Lio/peakmood/mobile/TerrainModel;->bucketCoordinate(DD)Lio/peakmood/mobile/TerrainModel$BucketCoordinate;

    move-result-object v2

    .line 160
    iget v3, v2, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;->latIndex:I

    iget v2, v2, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;->lonIndex:I

    invoke-static {v3, v2}, Lio/peakmood/mobile/TerrainModel;->bucketKey(II)J

    move-result-wide v2

    .line 161
    invoke-static {v2, v3}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v4

    invoke-interface {v0, v4}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/util/List;

    .line 162
    if-nez v4, :cond_0

    .line 163
    new-instance v4, Ljava/util/ArrayList;

    invoke-direct {v4}, Ljava/util/ArrayList;-><init>()V

    .line 164
    invoke-static {v2, v3}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v2

    invoke-interface {v0, v2, v4}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 166
    :cond_0
    invoke-interface {v4, v1}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 167
    goto :goto_0

    .line 168
    :cond_1
    return-object v0
.end method

.method public static getInstance(Landroid/content/Context;)Lio/peakmood/mobile/TerrainModel;
    .locals 2

    .line 35
    sget-object v0, Lio/peakmood/mobile/TerrainModel;->instance:Lio/peakmood/mobile/TerrainModel;

    .line 36
    if-eqz v0, :cond_0

    .line 37
    return-object v0

    .line 39
    :cond_0
    const-class v0, Lio/peakmood/mobile/TerrainModel;

    monitor-enter v0

    .line 40
    :try_start_0
    sget-object v1, Lio/peakmood/mobile/TerrainModel;->instance:Lio/peakmood/mobile/TerrainModel;

    if-nez v1, :cond_1

    .line 41
    new-instance v1, Lio/peakmood/mobile/TerrainModel;

    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    invoke-direct {v1, p0}, Lio/peakmood/mobile/TerrainModel;-><init>(Landroid/content/Context;)V

    sput-object v1, Lio/peakmood/mobile/TerrainModel;->instance:Lio/peakmood/mobile/TerrainModel;

    .line 43
    :cond_1
    sget-object p0, Lio/peakmood/mobile/TerrainModel;->instance:Lio/peakmood/mobile/TerrainModel;

    monitor-exit v0

    return-object p0

    .line 44
    :catchall_0
    move-exception p0

    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    throw p0
.end method

.method private globalReliefElevationM(DD)I
    .locals 17

    .line 194
    move-object/from16 v0, p0

    invoke-static/range {p3 .. p4}, Lio/peakmood/mobile/TerrainModel;->normalizeLon(D)D

    move-result-wide v1

    .line 195
    const-wide v3, 0x4066800000000000L    # 180.0

    cmpl-double v5, v1, v3

    if-nez v5, :cond_0

    .line 196
    const-wide v1, -0x3f99800000000000L    # -180.0

    .line 199
    :cond_0
    const-wide v5, 0x4056800000000000L    # 90.0

    sub-double v5, v5, p1

    div-double/2addr v5, v3

    const-wide v7, 0x40967c0000000000L    # 1439.0

    mul-double v5, v5, v7

    .line 200
    add-double/2addr v1, v3

    const-wide v3, 0x4076800000000000L    # 360.0

    div-double/2addr v1, v3

    const-wide v3, 0x40a6800000000000L    # 2880.0

    mul-double v1, v1, v3

    .line 201
    const-wide/16 v3, 0x0

    cmpg-double v9, v5, v3

    if-gez v9, :cond_1

    move-wide v7, v3

    goto :goto_0

    :cond_1
    cmpl-double v3, v5, v7

    if-lez v3, :cond_2

    goto :goto_0

    :cond_2
    move-wide v7, v5

    .line 203
    :goto_0
    invoke-static {v7, v8}, Ljava/lang/Math;->floor(D)D

    move-result-wide v3

    double-to-int v3, v3

    .line 204
    add-int/lit8 v4, v3, 0x1

    const/16 v5, 0x59f

    invoke-static {v4, v5}, Ljava/lang/Math;->min(II)I

    move-result v4

    .line 205
    invoke-static {v1, v2}, Ljava/lang/Math;->floor(D)D

    move-result-wide v5

    double-to-int v5, v5

    rem-int/lit16 v5, v5, 0xb40

    .line 206
    if-gez v5, :cond_3

    .line 207
    add-int/lit16 v5, v5, 0xb40

    .line 209
    :cond_3
    add-int/lit8 v6, v5, 0x1

    rem-int/lit16 v6, v6, 0xb40

    .line 210
    int-to-double v9, v3

    invoke-static {v9, v10}, Ljava/lang/Double;->isNaN(D)Z

    sub-double v15, v7, v9

    .line 211
    invoke-static {v1, v2}, Ljava/lang/Math;->floor(D)D

    move-result-wide v7

    sub-double v13, v1, v7

    .line 213
    iget-object v1, v0, Lio/peakmood/mobile/TerrainModel;->globalReliefBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {v1, v5, v3}, Landroid/graphics/Bitmap;->getPixel(II)I

    move-result v1

    and-int/lit16 v1, v1, 0xff

    int-to-double v9, v1

    .line 214
    iget-object v1, v0, Lio/peakmood/mobile/TerrainModel;->globalReliefBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {v1, v6, v3}, Landroid/graphics/Bitmap;->getPixel(II)I

    move-result v1

    and-int/lit16 v1, v1, 0xff

    int-to-double v11, v1

    .line 215
    iget-object v1, v0, Lio/peakmood/mobile/TerrainModel;->globalReliefBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {v1, v5, v4}, Landroid/graphics/Bitmap;->getPixel(II)I

    move-result v1

    and-int/lit16 v1, v1, 0xff

    int-to-double v1, v1

    .line 216
    iget-object v3, v0, Lio/peakmood/mobile/TerrainModel;->globalReliefBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {v3, v6, v4}, Landroid/graphics/Bitmap;->getPixel(II)I

    move-result v3

    and-int/lit16 v3, v3, 0xff

    int-to-double v3, v3

    .line 217
    invoke-static/range {v9 .. v14}, Lio/peakmood/mobile/TerrainModel;->lerp(DDD)D

    move-result-wide v5

    .line 218
    move-wide v9, v1

    move-wide v11, v3

    invoke-static/range {v9 .. v14}, Lio/peakmood/mobile/TerrainModel;->lerp(DDD)D

    move-result-wide v13

    .line 219
    move-wide v11, v5

    invoke-static/range {v11 .. v16}, Lio/peakmood/mobile/TerrainModel;->lerp(DDD)D

    move-result-wide v1

    .line 220
    const-wide/high16 v3, 0x4060000000000000L    # 128.0

    sub-double/2addr v1, v3

    const-wide v3, 0x40f3ca7000000000L    # 81063.0

    mul-double v1, v1, v3

    invoke-static {v1, v2}, Ljava/lang/Math;->round(D)J

    move-result-wide v1

    long-to-int v2, v1

    invoke-static {v2}, Lio/peakmood/mobile/TerrainModel;->roundMilliMetersToMeters(I)I

    move-result v1

    return v1
.end method

.method private static haversineKm(DDDD)D
    .locals 4

    .line 235
    nop

    .line 236
    invoke-static {p0, p1}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide v0

    .line 237
    invoke-static {p4, p5}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide v2

    .line 238
    sub-double/2addr p4, p0

    invoke-static {p4, p5}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide p0

    .line 239
    sub-double/2addr p6, p2

    invoke-static {p6, p7}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide p2

    .line 241
    const-wide/high16 p4, 0x4000000000000000L    # 2.0

    div-double/2addr p0, p4

    .line 242
    invoke-static {p0, p1}, Ljava/lang/Math;->sin(D)D

    move-result-wide p6

    invoke-static {p0, p1}, Ljava/lang/Math;->sin(D)D

    move-result-wide p0

    mul-double p6, p6, p0

    .line 243
    invoke-static {v0, v1}, Ljava/lang/Math;->cos(D)D

    move-result-wide p0

    invoke-static {v2, v3}, Ljava/lang/Math;->cos(D)D

    move-result-wide v0

    mul-double p0, p0, v0

    div-double/2addr p2, p4

    invoke-static {p2, p3}, Ljava/lang/Math;->sin(D)D

    move-result-wide p4

    mul-double p0, p0, p4

    invoke-static {p2, p3}, Ljava/lang/Math;->sin(D)D

    move-result-wide p2

    mul-double p0, p0, p2

    add-double/2addr p6, p0

    .line 244
    invoke-static {p6, p7}, Ljava/lang/Math;->sqrt(D)D

    move-result-wide p0

    const-wide/high16 p2, 0x3ff0000000000000L    # 1.0

    sub-double/2addr p2, p6

    invoke-static {p2, p3}, Ljava/lang/Math;->sqrt(D)D

    move-result-wide p2

    invoke-static {p0, p1, p2, p3}, Ljava/lang/Math;->atan2(DD)D

    move-result-wide p0

    const-wide p2, 0x40c8e30000000000L    # 12742.0

    mul-double p2, p2, p0

    return-wide p2
.end method

.method private static lerp(DDD)D
    .locals 0

    .line 231
    sub-double/2addr p2, p0

    mul-double p2, p2, p4

    add-double/2addr p0, p2

    return-wide p0
.end method

.method private loadGlobalReliefBitmap(Landroid/content/res/Resources;)Landroid/graphics/Bitmap;
    .locals 3

    .line 134
    new-instance v0, Landroid/graphics/BitmapFactory$Options;

    invoke-direct {v0}, Landroid/graphics/BitmapFactory$Options;-><init>()V

    .line 135
    const/4 v1, 0x0

    iput-boolean v1, v0, Landroid/graphics/BitmapFactory$Options;->inScaled:Z

    .line 137
    const/high16 v1, 0x7f040000

    :try_start_0
    invoke-virtual {p1, v1}, Landroid/content/res/Resources;->openRawResource(I)Ljava/io/InputStream;

    move-result-object p1
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    .line 138
    const/4 v1, 0x0

    :try_start_1
    invoke-static {p1, v1, v0}, Landroid/graphics/BitmapFactory;->decodeStream(Ljava/io/InputStream;Landroid/graphics/Rect;Landroid/graphics/BitmapFactory$Options;)Landroid/graphics/Bitmap;

    move-result-object v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 139
    if-eqz p1, :cond_0

    :try_start_2
    invoke-virtual {p1}, Ljava/io/InputStream;->close()V
    :try_end_2
    .catch Ljava/io/IOException; {:try_start_2 .. :try_end_2} :catch_0

    .line 141
    :cond_0
    nop

    .line 142
    if-eqz v0, :cond_2

    .line 145
    invoke-virtual {v0}, Landroid/graphics/Bitmap;->getWidth()I

    move-result p1

    const/16 v1, 0xb40

    if-ne p1, v1, :cond_1

    invoke-virtual {v0}, Landroid/graphics/Bitmap;->getHeight()I

    move-result p1

    const/16 v1, 0x5a0

    if-ne p1, v1, :cond_1

    .line 153
    return-object v0

    .line 146
    :cond_1
    new-instance p1, Ljava/lang/IllegalStateException;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Unexpected global relief dimensions: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    .line 148
    invoke-virtual {v0}, Landroid/graphics/Bitmap;->getWidth()I

    move-result v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "x"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    .line 150
    invoke-virtual {v0}, Landroid/graphics/Bitmap;->getHeight()I

    move-result v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {p1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 143
    :cond_2
    new-instance p1, Ljava/lang/IllegalStateException;

    const-string v0, "Unable to decode global relief map"

    invoke-direct {p1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 137
    :catchall_0
    move-exception v0

    if-eqz p1, :cond_3

    :try_start_3
    invoke-virtual {p1}, Ljava/io/InputStream;->close()V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    goto :goto_0

    :catchall_1
    move-exception p1

    :try_start_4
    invoke-static {v0, p1}, Lio/peakmood/mobile/MainActivity$$ExternalSyntheticBackport0;->m(Ljava/lang/Throwable;Ljava/lang/Throwable;)V

    :cond_3
    :goto_0
    throw v0
    :try_end_4
    .catch Ljava/io/IOException; {:try_start_4 .. :try_end_4} :catch_0

    .line 139
    :catch_0
    move-exception p1

    .line 140
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "Unable to load global relief map"

    invoke-direct {v0, v1, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;Ljava/lang/Throwable;)V

    throw v0
.end method

.method private loadSpecialAnchors(Landroid/content/res/Resources;Ljava/util/List;)V
    .locals 16
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroid/content/res/Resources;",
            "Ljava/util/List<",
            "Lio/peakmood/mobile/TerrainModel$ReliefAnchor;",
            ">;)V"
        }
    .end annotation

    .line 104
    const v0, 0x7f040001

    move-object/from16 v1, p1

    invoke-virtual {v1, v0}, Landroid/content/res/Resources;->openRawResource(I)Ljava/io/InputStream;

    move-result-object v0

    .line 105
    :try_start_0
    new-instance v1, Ljava/io/BufferedReader;

    new-instance v2, Ljava/io/InputStreamReader;

    sget-object v3, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v2, v0, v3}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;Ljava/nio/charset/Charset;)V

    invoke-direct {v1, v2}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    .line 107
    const/4 v0, 0x0

    const/4 v2, 0x0

    .line 108
    :goto_0
    :try_start_1
    invoke-virtual {v1}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v3

    if-eqz v3, :cond_3

    .line 109
    const/4 v4, 0x1

    add-int/2addr v2, v4

    .line 110
    invoke-virtual {v3}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v3

    .line 111
    invoke-virtual {v3}, Ljava/lang/String;->isEmpty()Z

    move-result v5

    if-nez v5, :cond_2

    const-string v5, "#"

    invoke-virtual {v3, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v5

    if-eqz v5, :cond_0

    .line 112
    move-object/from16 v3, p2

    goto :goto_0

    .line 114
    :cond_0
    const-string v5, "\\|"

    invoke-virtual {v3, v5}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v3

    .line 115
    array-length v5, v3

    const/4 v6, 0x5

    if-ne v5, v6, :cond_1

    .line 118
    new-instance v7, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    aget-object v5, v3, v0

    .line 120
    invoke-virtual {v5}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v8

    aget-object v4, v3, v4

    .line 121
    invoke-virtual {v4}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4}, Ljava/lang/Double;->parseDouble(Ljava/lang/String;)D

    move-result-wide v9

    const/4 v4, 0x2

    aget-object v4, v3, v4

    .line 122
    invoke-virtual {v4}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4}, Ljava/lang/Double;->parseDouble(Ljava/lang/String;)D

    move-result-wide v11

    const/4 v4, 0x3

    aget-object v4, v3, v4

    .line 123
    invoke-virtual {v4}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result v13

    const/4 v4, 0x4

    aget-object v3, v3, v4

    .line 124
    invoke-virtual {v3}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v3

    invoke-static {v3}, Ljava/lang/Double;->parseDouble(Ljava/lang/String;)D

    move-result-wide v14

    invoke-direct/range {v7 .. v15}, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;-><init>(Ljava/lang/String;DDID)V

    .line 118
    move-object/from16 v3, p2

    invoke-interface {v3, v7}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 127
    goto :goto_0

    .line 116
    :cond_1
    new-instance v0, Ljava/lang/IllegalStateException;

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Bad terrain row on line "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v0, v2}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 111
    :cond_2
    move-object/from16 v3, p2

    goto :goto_0

    .line 128
    :cond_3
    :try_start_2
    invoke-virtual {v1}, Ljava/io/BufferedReader;->close()V
    :try_end_2
    .catch Ljava/io/IOException; {:try_start_2 .. :try_end_2} :catch_0

    .line 130
    nop

    .line 131
    return-void

    .line 105
    :catchall_0
    move-exception v0

    move-object v2, v0

    :try_start_3
    invoke-virtual {v1}, Ljava/io/BufferedReader;->close()V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    goto :goto_1

    :catchall_1
    move-exception v0

    :try_start_4
    invoke-static {v2, v0}, Lio/peakmood/mobile/MainActivity$$ExternalSyntheticBackport0;->m(Ljava/lang/Throwable;Ljava/lang/Throwable;)V

    :goto_1
    throw v2
    :try_end_4
    .catch Ljava/io/IOException; {:try_start_4 .. :try_end_4} :catch_0

    .line 128
    :catch_0
    move-exception v0

    .line 129
    new-instance v1, Ljava/lang/IllegalStateException;

    const-string v2, "Unable to load terrain anchors"

    invoke-direct {v1, v2, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;Ljava/lang/Throwable;)V

    goto :goto_3

    :goto_2
    throw v1

    :goto_3
    goto :goto_2
.end method

.method private nearestAnchor(DD)Lio/peakmood/mobile/TerrainModel$AnchorMatch;
    .locals 26

    .line 67
    move-object/from16 v0, p0

    invoke-static/range {p1 .. p4}, Lio/peakmood/mobile/TerrainModel;->bucketCoordinate(DD)Lio/peakmood/mobile/TerrainModel$BucketCoordinate;

    move-result-object v1

    .line 68
    nop

    .line 69
    nop

    .line 70
    const/4 v2, 0x0

    const-wide/high16 v3, 0x7ff0000000000000L    # Double.POSITIVE_INFINITY

    const/4 v5, -0x1

    const/4 v6, -0x1

    :goto_0
    const/4 v7, 0x1

    if-gt v6, v7, :cond_5

    .line 71
    iget v8, v1, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;->latIndex:I

    add-int/2addr v8, v6

    .line 72
    if-ltz v8, :cond_4

    const/16 v9, 0x1e

    if-lt v8, v9, :cond_0

    .line 73
    goto :goto_4

    .line 75
    :cond_0
    const/4 v9, -0x1

    :goto_1
    if-gt v9, v7, :cond_4

    .line 76
    iget v10, v1, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;->lonIndex:I

    add-int/2addr v10, v9

    add-int/lit8 v10, v10, 0x3c

    rem-int/lit8 v10, v10, 0x3c

    .line 77
    iget-object v11, v0, Lio/peakmood/mobile/TerrainModel;->anchorIndex:Ljava/util/Map;

    invoke-static {v8, v10}, Lio/peakmood/mobile/TerrainModel;->bucketKey(II)J

    move-result-wide v12

    invoke-static {v12, v13}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v10

    invoke-interface {v11, v10}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v10

    check-cast v10, Ljava/util/List;

    .line 78
    if-nez v10, :cond_1

    .line 79
    goto :goto_3

    .line 81
    :cond_1
    invoke-interface {v10}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v10

    :goto_2
    invoke-interface {v10}, Ljava/util/Iterator;->hasNext()Z

    move-result v11

    if-eqz v11, :cond_3

    invoke-interface {v10}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v11

    check-cast v11, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    .line 82
    iget-wide v12, v11, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lat:D

    iget-wide v14, v11, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lon:D

    move-wide/from16 v16, v12

    move-wide/from16 v18, v14

    move-wide/from16 v12, p1

    move-wide/from16 v14, p3

    invoke-static/range {v12 .. v19}, Lio/peakmood/mobile/TerrainModel;->haversineKm(DDDD)D

    move-result-wide v16

    .line 83
    cmpg-double v12, v16, v3

    if-gez v12, :cond_2

    .line 84
    nop

    .line 85
    move-object v2, v11

    move-wide/from16 v3, v16

    .line 87
    :cond_2
    goto :goto_2

    .line 75
    :cond_3
    :goto_3
    add-int/lit8 v9, v9, 0x1

    goto :goto_1

    .line 70
    :cond_4
    :goto_4
    add-int/lit8 v6, v6, 0x1

    goto :goto_0

    .line 90
    :cond_5
    if-eqz v2, :cond_6

    .line 91
    new-instance v1, Lio/peakmood/mobile/TerrainModel$AnchorMatch;

    invoke-direct {v1, v2, v3, v4}, Lio/peakmood/mobile/TerrainModel$AnchorMatch;-><init>(Lio/peakmood/mobile/TerrainModel$ReliefAnchor;D)V

    return-object v1

    .line 93
    :cond_6
    iget-object v1, v0, Lio/peakmood/mobile/TerrainModel;->anchors:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v1

    :goto_5
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_8

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    .line 94
    iget-wide v6, v5, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lat:D

    iget-wide v8, v5, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lon:D

    move-wide/from16 v18, p1

    move-wide/from16 v20, p3

    move-wide/from16 v22, v6

    move-wide/from16 v24, v8

    invoke-static/range {v18 .. v25}, Lio/peakmood/mobile/TerrainModel;->haversineKm(DDDD)D

    move-result-wide v6

    .line 95
    cmpg-double v8, v6, v3

    if-gez v8, :cond_7

    .line 96
    nop

    .line 97
    move-object v2, v5

    move-wide v3, v6

    .line 99
    :cond_7
    goto :goto_5

    .line 100
    :cond_8
    new-instance v1, Lio/peakmood/mobile/TerrainModel$AnchorMatch;

    invoke-direct {v1, v2, v3, v4}, Lio/peakmood/mobile/TerrainModel$AnchorMatch;-><init>(Lio/peakmood/mobile/TerrainModel$ReliefAnchor;D)V

    return-object v1
.end method

.method private static normalizeLon(D)D
    .locals 7

    .line 182
    const-wide v0, 0x4066800000000000L    # 180.0

    add-double v2, p0, v0

    const-wide v4, 0x4076800000000000L    # 360.0

    rem-double/2addr v2, v4

    add-double/2addr v2, v4

    rem-double/2addr v2, v4

    sub-double/2addr v2, v0

    .line 183
    const-wide v4, -0x3f99800000000000L    # -180.0

    cmpl-double v6, v2, v4

    if-nez v6, :cond_0

    const-wide/16 v4, 0x0

    cmpl-double v6, p0, v4

    if-lez v6, :cond_0

    .line 184
    return-wide v0

    .line 186
    :cond_0
    return-wide v2
.end method

.method private static roundMilliMetersToMeters(I)I
    .locals 0

    .line 224
    if-ltz p0, :cond_0

    .line 225
    add-int/lit16 p0, p0, 0x1f4

    div-int/lit16 p0, p0, 0x3e8

    return p0

    .line 227
    :cond_0
    neg-int p0, p0

    add-int/lit16 p0, p0, 0x1f4

    div-int/lit16 p0, p0, 0x3e8

    neg-int p0, p0

    return p0
.end method


# virtual methods
.method public snapshot(DDD)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;
    .locals 2

    .line 56
    invoke-direct {p0, p1, p2, p3, p4}, Lio/peakmood/mobile/TerrainModel;->nearestAnchor(DD)Lio/peakmood/mobile/TerrainModel$AnchorMatch;

    move-result-object p5

    .line 57
    invoke-direct {p0, p1, p2, p3, p4}, Lio/peakmood/mobile/TerrainModel;->globalReliefElevationM(DD)I

    move-result p1

    .line 58
    nop

    .line 59
    iget-object p2, p5, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->anchor:Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    if-eqz p2, :cond_0

    iget-wide p2, p5, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->distanceKm:D

    iget-object p4, p5, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->anchor:Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    iget-wide v0, p4, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->radiusKm:D

    cmpg-double p4, p2, v0

    if-gtz p4, :cond_0

    .line 60
    iget-object p1, p5, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->anchor:Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    iget p1, p1, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->elevationM:I

    .line 61
    iget-object p2, p5, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->anchor:Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    iget-object p2, p2, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->name:Ljava/lang/String;

    goto :goto_0

    .line 63
    :cond_0
    const-string p2, "Global Relief Cache"

    :goto_0
    new-instance p3, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;

    invoke-direct {p3, p2, p1}, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;-><init>(Ljava/lang/String;I)V

    return-object p3
.end method
