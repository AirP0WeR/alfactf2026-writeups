.class final Lio/peakmood/mobile/MiningSceneView$Shard;
.super Ljava/lang/Object;
.source "MiningSceneView.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lio/peakmood/mobile/MiningSceneView;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "Shard"
.end annotation


# instance fields
.field final angle:F

.field final color:I

.field final speed:F

.field final startedAtMs:J


# direct methods
.method constructor <init>(FFJI)V
    .locals 0

    .line 377
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 378
    iput p1, p0, Lio/peakmood/mobile/MiningSceneView$Shard;->angle:F

    .line 379
    iput p2, p0, Lio/peakmood/mobile/MiningSceneView$Shard;->speed:F

    .line 380
    iput-wide p3, p0, Lio/peakmood/mobile/MiningSceneView$Shard;->startedAtMs:J

    .line 381
    iput p5, p0, Lio/peakmood/mobile/MiningSceneView$Shard;->color:I

    .line 382
    return-void
.end method
