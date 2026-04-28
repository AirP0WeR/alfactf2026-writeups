.class final Lio/peakmood/mobile/TerrainModel$AnchorMatch;
.super Ljava/lang/Object;
.source "TerrainModel.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lio/peakmood/mobile/TerrainModel;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "AnchorMatch"
.end annotation


# instance fields
.field final anchor:Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

.field final distanceKm:D


# direct methods
.method constructor <init>(Lio/peakmood/mobile/TerrainModel$ReliefAnchor;D)V
    .locals 0

    .line 267
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 268
    iput-object p1, p0, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->anchor:Lio/peakmood/mobile/TerrainModel$ReliefAnchor;

    .line 269
    iput-wide p2, p0, Lio/peakmood/mobile/TerrainModel$AnchorMatch;->distanceKm:D

    .line 270
    return-void
.end method
