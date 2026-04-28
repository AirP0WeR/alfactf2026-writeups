.class final Lio/peakmood/mobile/TerrainModel$BucketCoordinate;
.super Ljava/lang/Object;
.source "TerrainModel.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lio/peakmood/mobile/TerrainModel;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "BucketCoordinate"
.end annotation


# instance fields
.field final latIndex:I

.field final lonIndex:I


# direct methods
.method constructor <init>(II)V
    .locals 0

    .line 277
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 278
    iput p1, p0, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;->latIndex:I

    .line 279
    iput p2, p0, Lio/peakmood/mobile/TerrainModel$BucketCoordinate;->lonIndex:I

    .line 280
    return-void
.end method
