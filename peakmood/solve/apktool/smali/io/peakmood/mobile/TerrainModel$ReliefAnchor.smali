.class final Lio/peakmood/mobile/TerrainModel$ReliefAnchor;
.super Ljava/lang/Object;
.source "TerrainModel.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lio/peakmood/mobile/TerrainModel;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "ReliefAnchor"
.end annotation


# instance fields
.field final elevationM:I

.field final lat:D

.field final lon:D

.field final name:Ljava/lang/String;

.field final radiusKm:D


# direct methods
.method constructor <init>(Ljava/lang/String;DDID)V
    .locals 0

    .line 254
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 255
    iput-object p1, p0, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->name:Ljava/lang/String;

    .line 256
    iput-wide p2, p0, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lat:D

    .line 257
    iput-wide p4, p0, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->lon:D

    .line 258
    iput p6, p0, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->elevationM:I

    .line 259
    iput-wide p7, p0, Lio/peakmood/mobile/TerrainModel$ReliefAnchor;->radiusKm:D

    .line 260
    return-void
.end method
