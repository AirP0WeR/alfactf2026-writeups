.class Lio/peakmood/mobile/MainActivity$10;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->showConnectionFailure()V
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

    .line 797
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 800
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$802(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 801
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$702(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)Ljava/lang/String;

    .line 802
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$900(Lio/peakmood/mobile/MainActivity;)V

    .line 803
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    const v2, 0x7f060019

    invoke-virtual {v1, v2}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object v1

    const-string v2, "\u041d\u0415\u0422 \u0421\u0412\u042f\u0417\u0418"

    const-string v3, "\u0421\u0435\u0440\u0432\u0438\u0441 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u0435\u043d"

    invoke-static {v0, v3, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 804
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$10;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$2700(Lio/peakmood/mobile/MainActivity;)V

    .line 805
    return-void
.end method
