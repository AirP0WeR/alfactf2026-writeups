.class Lio/peakmood/mobile/WorldMapView$2;
.super Ljava/lang/Object;
.source "WorldMapView.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/WorldMapView;->queueTileFetch(Ljava/lang/String;IIILjava/io/File;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lio/peakmood/mobile/WorldMapView;

.field final synthetic val$cachedFile:Ljava/io/File;

.field final synthetic val$key:Ljava/lang/String;

.field final synthetic val$tileX:I

.field final synthetic val$tileY:I

.field final synthetic val$zoom:I


# direct methods
.method constructor <init>(Lio/peakmood/mobile/WorldMapView;IIILjava/io/File;Ljava/lang/String;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x1010,
            0x1010,
            0x1010,
            0x1010,
            0x1010
        }
        names = {
            null,
            null,
            null,
            null,
            null,
            null
        }
    .end annotation

    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 493
    iput-object p1, p0, Lio/peakmood/mobile/WorldMapView$2;->this$0:Lio/peakmood/mobile/WorldMapView;

    iput p2, p0, Lio/peakmood/mobile/WorldMapView$2;->val$zoom:I

    iput p3, p0, Lio/peakmood/mobile/WorldMapView$2;->val$tileX:I

    iput p4, p0, Lio/peakmood/mobile/WorldMapView$2;->val$tileY:I

    iput-object p5, p0, Lio/peakmood/mobile/WorldMapView$2;->val$cachedFile:Ljava/io/File;

    iput-object p6, p0, Lio/peakmood/mobile/WorldMapView$2;->val$key:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 5

    .line 497
    :try_start_0
    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView$2;->this$0:Lio/peakmood/mobile/WorldMapView;

    iget v1, p0, Lio/peakmood/mobile/WorldMapView$2;->val$zoom:I

    iget v2, p0, Lio/peakmood/mobile/WorldMapView$2;->val$tileX:I

    iget v3, p0, Lio/peakmood/mobile/WorldMapView$2;->val$tileY:I

    iget-object v4, p0, Lio/peakmood/mobile/WorldMapView$2;->val$cachedFile:Ljava/io/File;

    invoke-static {v0, v1, v2, v3, v4}, Lio/peakmood/mobile/WorldMapView;->access$000(Lio/peakmood/mobile/WorldMapView;IIILjava/io/File;)V

    .line 498
    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView$2;->val$cachedFile:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Landroid/graphics/BitmapFactory;->decodeFile(Ljava/lang/String;)Landroid/graphics/Bitmap;

    move-result-object v0

    .line 499
    if-eqz v0, :cond_0

    .line 500
    invoke-static {}, Lio/peakmood/mobile/WorldMapView;->access$100()Ljava/util/Map;

    move-result-object v1

    iget-object v2, p0, Lio/peakmood/mobile/WorldMapView$2;->val$key:Ljava/lang/String;

    invoke-interface {v1, v2, v0}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 505
    :cond_0
    :goto_0
    invoke-static {}, Lio/peakmood/mobile/WorldMapView;->access$200()Ljava/util/Set;

    move-result-object v0

    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView$2;->val$key:Ljava/lang/String;

    invoke-interface {v0, v1}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    .line 506
    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView$2;->this$0:Lio/peakmood/mobile/WorldMapView;

    invoke-virtual {v0}, Lio/peakmood/mobile/WorldMapView;->postInvalidateOnAnimation()V

    .line 507
    goto :goto_1

    .line 505
    :catchall_0
    move-exception v0

    goto :goto_2

    .line 502
    :catch_0
    move-exception v0

    .line 503
    :try_start_1
    const-string v1, "WorldMapView"

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Tile fetch failed for "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    iget-object v3, p0, Lio/peakmood/mobile/WorldMapView$2;->val$key:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v1, v2, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_0

    .line 508
    :goto_1
    return-void

    .line 505
    :goto_2
    invoke-static {}, Lio/peakmood/mobile/WorldMapView;->access$200()Ljava/util/Set;

    move-result-object v1

    iget-object v2, p0, Lio/peakmood/mobile/WorldMapView$2;->val$key:Ljava/lang/String;

    invoke-interface {v1, v2}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    .line 506
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView$2;->this$0:Lio/peakmood/mobile/WorldMapView;

    invoke-virtual {v1}, Lio/peakmood/mobile/WorldMapView;->postInvalidateOnAnimation()V

    .line 507
    goto :goto_4

    :goto_3
    throw v0

    :goto_4
    goto :goto_3
.end method
