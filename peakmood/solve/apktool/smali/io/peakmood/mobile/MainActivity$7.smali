.class Lio/peakmood/mobile/MainActivity$7;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->hitNode()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lio/peakmood/mobile/MainActivity;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010
        }
        names = {
            null
        }
    .end annotation

    .line 618
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 5

    .line 622
    const v0, 0x7f060019

    :try_start_0
    new-instance v1, Lorg/json/JSONObject;

    invoke-direct {v1}, Lorg/json/JSONObject;-><init>()V

    .line 623
    const-string v2, "node_id"

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v3}, Lio/peakmood/mobile/MainActivity;->access$100(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v2, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    .line 624
    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    const-string v3, "/api/v1/node/hit"

    iget-object v4, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v4}, Lio/peakmood/mobile/MainActivity;->access$700(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;

    move-result-object v4

    invoke-static {v2, v3, v1, v4}, Lio/peakmood/mobile/MainActivity;->access$600(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    .line 625
    const-string v2, "_http_status"

    const/16 v3, 0xc8

    invoke-virtual {v1, v2, v3}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v2

    .line 626
    const/16 v3, 0x190

    if-lt v2, v3, :cond_0

    .line 627
    const-string v3, "error"

    iget-object v4, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-virtual {v4, v0}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v1, v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 628
    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    new-instance v4, Lio/peakmood/mobile/MainActivity$7$1;

    invoke-direct {v4, p0, v2, v1}, Lio/peakmood/mobile/MainActivity$7$1;-><init>(Lio/peakmood/mobile/MainActivity$7;ILjava/lang/String;)V

    invoke-virtual {v3, v4}, Lio/peakmood/mobile/MainActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 640
    return-void

    .line 642
    :cond_0
    const-string v2, "node"

    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    .line 643
    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    new-instance v3, Lio/peakmood/mobile/MainActivity$7$2;

    invoke-direct {v3, p0, v1}, Lio/peakmood/mobile/MainActivity$7$2;-><init>(Lio/peakmood/mobile/MainActivity$7;Lorg/json/JSONObject;)V

    invoke-virtual {v2, v3}, Lio/peakmood/mobile/MainActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 665
    goto :goto_0

    .line 663
    :catch_0
    move-exception v1

    .line 664
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-virtual {v2, v0}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object v0

    invoke-static {v1, v0}, Lio/peakmood/mobile/MainActivity;->access$1500(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V

    .line 666
    :goto_0
    return-void
.end method
