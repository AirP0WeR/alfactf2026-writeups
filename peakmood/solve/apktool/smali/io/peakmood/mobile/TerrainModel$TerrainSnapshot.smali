.class public final Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;
.super Ljava/lang/Object;
.source "TerrainModel.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lio/peakmood/mobile/TerrainModel;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x19
    name = "TerrainSnapshot"
.end annotation


# instance fields
.field public final expectedElevationM:I

.field public final label:Ljava/lang/String;


# direct methods
.method constructor <init>(Ljava/lang/String;I)V
    .locals 0

    .line 287
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 288
    iput-object p1, p0, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->label:Ljava/lang/String;

    .line 289
    iput p2, p0, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->expectedElevationM:I

    .line 290
    return-void
.end method
