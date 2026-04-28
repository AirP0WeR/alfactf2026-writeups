.class Lio/peakmood/mobile/MainActivity$6;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->submitScan(Landroid/location/Location;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lio/peakmood/mobile/MainActivity;

.field final synthetic val$location:Landroid/location/Location;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity;Landroid/location/Location;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x1010
        }
        names = {
            null,
            null
        }
    .end annotation

    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 455
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    iput-object p2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 7

    .line 459
    :try_start_0
    new-instance v0, Lorg/json/JSONObject;

    invoke-direct {v0}, Lorg/json/JSONObject;-><init>()V

    .line 460
    const-string v1, "lat"

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-virtual {v2}, Landroid/location/Location;->getLatitude()D

    move-result-wide v2

    invoke-virtual {v0, v1, v2, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;D)Lorg/json/JSONObject;

    .line 461
    const-string v1, "lon"

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-virtual {v2}, Landroid/location/Location;->getLongitude()D

    move-result-wide v2

    invoke-virtual {v0, v1, v2, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;D)Lorg/json/JSONObject;

    .line 462
    const-string v1, "reported_alt_m"

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-virtual {v2}, Landroid/location/Location;->hasAltitude()Z

    move-result v2

    const-wide/16 v3, 0x0

    if-eqz v2, :cond_0

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-virtual {v2}, Landroid/location/Location;->getAltitude()D

    move-result-wide v5

    goto :goto_0

    :cond_0
    move-wide v5, v3

    :goto_0
    invoke-virtual {v0, v1, v5, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;D)Lorg/json/JSONObject;

    .line 463
    const-string v1, "vertical_accuracy_m"

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-virtual {v2}, Landroid/location/Location;->hasVerticalAccuracy()Z

    move-result v2

    if-eqz v2, :cond_1

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->val$location:Landroid/location/Location;

    invoke-virtual {v2}, Landroid/location/Location;->getVerticalAccuracyMeters()F

    move-result v2

    float-to-double v3, v2

    :cond_1
    invoke-virtual {v0, v1, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;D)Lorg/json/JSONObject;

    .line 465
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    const-string v2, "/api/v1/geo/update"

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v3}, Lio/peakmood/mobile/MainActivity;->access$700(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;

    move-result-object v3

    invoke-static {v1, v2, v0, v3}, Lio/peakmood/mobile/MainActivity;->access$600(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    .line 466
    const-string v1, "_http_status"

    const/16 v2, 0xc8

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v1

    .line 467
    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    new-instance v3, Lio/peakmood/mobile/MainActivity$6$1;

    invoke-direct {v3, p0, v1, v0}, Lio/peakmood/mobile/MainActivity$6$1;-><init>(Lio/peakmood/mobile/MainActivity$6;ILorg/json/JSONObject;)V

    invoke-virtual {v2, v3}, Lio/peakmood/mobile/MainActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 475
    goto :goto_1

    .line 473
    :catch_0
    move-exception v0

    .line 474
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    const v2, 0x7f060019

    invoke-virtual {v1, v2}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$1500(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V

    .line 476
    :goto_1
    return-void
.end method
